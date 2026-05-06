"""Wallet API views."""
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Wallet, Transaction, transfer_funds, process_payment


# ── Serializers ───────────────────────────────────────────────────────────────

class WalletSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Wallet
        fields = ('username', 'balance', 'currency', 'updated_at')


class TransactionSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'sender_name', 'receiver_name', 'amount',
                  'currency', 'transaction_type', 'status',
                  'description', 'created_at')


# ── Views ─────────────────────────────────────────────────────────────────────

class WalletBalanceView(APIView):
    """GET /api/wallet/balance/"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        wallet = Wallet.get_or_create_for_user(request.user)
        return Response(WalletSerializer(wallet).data)


class TransactionListView(APIView):
    """GET /api/wallet/transactions/"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        txns = Transaction.objects.filter(
            sender=request.user
        ) | Transaction.objects.filter(
            receiver=request.user
        )
        txns = txns.order_by('-created_at')[:50]
        return Response(TransactionSerializer(txns, many=True).data)


class TransferView(APIView):
    """POST /api/wallet/transfer/"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        username = request.data.get('username', '').strip()
        amount = request.data.get('amount')
        description = request.data.get('description', '')

        if not username or not amount:
            return Response(
                {'error': 'username and amount are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            receiver = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': f'User "{username}" not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        from decimal import Decimal, InvalidOperation
        try:
            amount = Decimal(str(amount))
        except InvalidOperation:
            return Response(
                {'error': 'Invalid amount.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success, message, txn = transfer_funds(
            request.user, receiver, amount, description
        )

        if success:
            wallet = Wallet.get_or_create_for_user(request.user)
            return Response({
                'success': True,
                'message': message,
                'transaction': TransactionSerializer(txn).data,
                'new_balance': str(wallet.balance),
            })
        else:
            return Response(
                {'success': False, 'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )


class PhoneTopupView(APIView):
    """POST /api/wallet/topup/"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        phone = request.data.get('phone', '').strip()
        amount = request.data.get('amount')

        if not phone or not amount:
            return Response(
                {'error': 'phone and amount are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from decimal import Decimal
        amount = Decimal(str(amount))

        success, message, txn = process_payment(
            request.user, amount,
            Transaction.TYPE_PHONE_TOPUP,
            description=f"Phone top-up: {phone}",
            reference=phone
        )

        if success:
            wallet = Wallet.get_or_create_for_user(request.user)
            return Response({
                'success': True,
                'message': message,
                'new_balance': str(wallet.balance),
            })
        else:
            return Response(
                {'success': False, 'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )


class BillPaymentView(APIView):
    """POST /api/wallet/pay-bill/"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        bill_type = request.data.get('bill_type', 'general')
        amount = request.data.get('amount')
        reference = request.data.get('reference', '')

        if not amount:
            return Response(
                {'error': 'amount is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from decimal import Decimal
        amount = Decimal(str(amount))

        success, message, txn = process_payment(
            request.user, amount,
            Transaction.TYPE_BILL_PAYMENT,
            description=f"Bill: {bill_type}",
            reference=reference
        )

        if success:
            wallet = Wallet.get_or_create_for_user(request.user)
            return Response({
                'success': True,
                'message': message,
                'new_balance': str(wallet.balance),
            })
        else:
            return Response(
                {'success': False, 'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
