"""Wallet API views."""
from decimal import Decimal, InvalidOperation

from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction, Wallet, process_payment, transfer_funds

User = get_user_model()


def clean_text(value):
    return str(value or "").strip()


def parse_amount(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return amount if amount > 0 else None


class WalletSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Wallet
        fields = ("username", "balance", "currency", "updated_at")


class TransactionSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.username", read_only=True)
    receiver_name = serializers.CharField(source="receiver.username", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "sender_name",
            "receiver_name",
            "amount",
            "currency",
            "transaction_type",
            "status",
            "description",
            "created_at",
        )


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
        txns = (
            Transaction.objects.filter(sender=request.user)
            | Transaction.objects.filter(receiver=request.user)
        )
        txns = txns.order_by("-created_at")[:50]
        return Response(TransactionSerializer(txns, many=True).data)


def verify_pin_or_error(user, request):
    """Returns a Response error if PIN check fails, else None."""
    pin = clean_text(request.data.get("pin", ""))
    if not user.has_pin:
        return Response({"error": "PIN not set. Please set your PIN first."}, status=403)
    if not pin:
        return Response({"error": "PIN required to confirm this operation."}, status=403)
    if not user.check_pin(pin):
        return Response({"error": "Incorrect PIN. Please try again."}, status=403)
    return None


class TransferView(APIView):
    """POST /api/wallet/transfer/"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        pin_err = verify_pin_or_error(request.user, request)
        if pin_err: return pin_err

        phone = clean_text(request.data.get("phone"))
        amount = request.data.get("amount")
        description = clean_text(request.data.get("description"))

        if not phone or not amount:
            return Response(
                {"error": "phone and amount are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            receiver = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"error": f'No account found with phone number "{phone}".'},
                status=status.HTTP_404_NOT_FOUND,
            )

        amount = parse_amount(amount)
        if amount is None:
            return Response(
                {"error": "Amount must be a positive number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message, txn = transfer_funds(
            request.user, receiver, amount, description
        )

        if success:
            wallet = Wallet.get_or_create_for_user(request.user)
            return Response(
                {
                    "success": True,
                    "message": message,
                    "transaction": TransactionSerializer(txn).data,
                    "new_balance": str(wallet.balance),
                }
            )

        return Response(
            {"success": False, "error": message},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PhoneTopupView(APIView):
    """POST /api/wallet/topup/"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        pin_err = verify_pin_or_error(request.user, request)
        if pin_err: return pin_err
        phone = clean_text(request.data.get("phone"))
        amount = request.data.get("amount")

        if not phone or not amount:
            return Response(
                {"error": "phone and amount are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = parse_amount(amount)
        if amount is None:
            return Response(
                {"error": "Amount must be a positive number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message, _ = process_payment(
            request.user,
            amount,
            Transaction.TYPE_PHONE_TOPUP,
            description=f"Phone top-up: {phone}",
            reference=phone,
        )

        if success:
            wallet = Wallet.get_or_create_for_user(request.user)
            return Response(
                {
                    "success": True,
                    "message": message,
                    "new_balance": str(wallet.balance),
                }
            )

        return Response(
            {"success": False, "error": message},
            status=status.HTTP_400_BAD_REQUEST,
        )


class BillPaymentView(APIView):
    """POST /api/wallet/pay-bill/"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        pin_err = verify_pin_or_error(request.user, request)
        if pin_err: return pin_err
        bill_type = clean_text(request.data.get("bill_type")) or "general"
        amount = request.data.get("amount")
        reference = clean_text(request.data.get("reference"))

        if not amount:
            return Response(
                {"error": "amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = parse_amount(amount)
        if amount is None:
            return Response(
                {"error": "Amount must be a positive number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message, _ = process_payment(
            request.user,
            amount,
            Transaction.TYPE_BILL_PAYMENT,
            description=f"Bill: {bill_type}",
            reference=reference,
        )

        if success:
            wallet = Wallet.get_or_create_for_user(request.user)
            return Response(
                {
                    "success": True,
                    "message": message,
                    "new_balance": str(wallet.balance),
                }
            )

        return Response(
            {"success": False, "error": message},
            status=status.HTTP_400_BAD_REQUEST,
        )
