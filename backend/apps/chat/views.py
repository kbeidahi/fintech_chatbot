"""Chat views — using multilingual engine."""
from django.utils import timezone
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatSession, Message
from .multilingual_engine import multilingual_engine


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'role', 'content', 'intent', 'confidence', 'created_at')


class SessionSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ('id', 'title', 'started_at', 'ended_at', 'message_count')

    def get_message_count(self, obj):
        return obj.messages.count()


class SessionDetailSerializer(SessionSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(SessionSerializer.Meta):
        fields = SessionSerializer.Meta.fields + ('messages',)


class SendMessageView(APIView):
    """POST /api/chat/message/"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_text = request.data.get('message', '').strip()
        if not user_text:
            return Response({'error': 'Message cannot be empty.'}, status=400)
        if len(user_text) > 1000:
            return Response({'error': 'Message too long.'}, status=400)

        session_id = request.data.get('session_id')
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({'error': 'Session not found.'}, status=404)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=user_text[:80],
            )

        user_msg = Message.objects.create(
            session=session,
            role='user',
            content=user_text,
        )

        # Use multilingual engine with user context for actions
        result = multilingual_engine.resolve(user_text, user=request.user)

        bot_msg = Message.objects.create(
            session=session,
            role='bot',
            content=result['answer'],
            intent=result.get('intent', ''),
            confidence=result.get('confidence', 1.0),
        )

        return Response({
            'session_id': str(session.id),
            'user_message': MessageSerializer(user_msg).data,
            'bot_message': MessageSerializer(bot_msg).data,
            'source': result.get('source', 'faq'),
            'lang': result.get('lang', 'en'),
            'action': result.get('action'),
        }, status=status.HTTP_200_OK)


class SessionListView(generics.ListAPIView):
    serializer_class = SessionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


class SessionDetailView(generics.RetrieveAPIView):
    serializer_class = SessionDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def get_object(self):
        return generics.get_object_or_404(
            self.get_queryset(), id=self.kwargs['pk']
        )


class EndSessionView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk):
        session = generics.get_object_or_404(
            ChatSession, id=pk, user=request.user, ended_at__isnull=True
        )
        session.ended_at = timezone.now()
        session.save()
        return Response({'status': 'ended'})
