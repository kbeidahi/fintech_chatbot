# apps/faq/views.py
from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated
from .models import FAQCategory, FAQItem


class FAQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQItem
        fields = ("id", "question", "answer")


class FAQCategorySerializer(serializers.ModelSerializer):
    items = FAQItemSerializer(many=True, read_only=True)

    class Meta:
        model = FAQCategory
        fields = ("id", "name", "icon", "items")


class FAQListView(generics.ListAPIView):
    """GET /api/faq/  — returns all categories with their FAQ items."""
    serializer_class = FAQCategorySerializer
    permission_classes = (IsAuthenticated,)
    queryset = FAQCategory.objects.prefetch_related("items").filter(items__is_active=True).distinct()
