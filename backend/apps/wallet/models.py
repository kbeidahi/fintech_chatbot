"""Wallet models — balance, transactions, and payments."""
import uuid
from django.db import models, transaction
from django.conf import settings


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    currency = models.CharField(max_length=3, default="MRU")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.balance} {self.currency}"

    def can_debit(self, amount):
        return self.is_active and self.balance >= amount

    @classmethod
    def get_or_create_for_user(cls, user):
        wallet, _ = cls.objects.get_or_create(
            user=user,
            defaults={"balance": 1000.00}
        )
        return wallet


class Transaction(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    TYPE_TRANSFER = "transfer"
    TYPE_DEPOSIT = "deposit"
    TYPE_WITHDRAWAL = "withdrawal"
    TYPE_PHONE_TOPUP = "phone_topup"
    TYPE_BILL_PAYMENT = "bill_payment"
    TYPE_PURCHASE = "purchase"
    TYPE_GIMTEL = "gimtel"
    TYPE_CHOICES = [
        (TYPE_TRANSFER, "Transfer"),
        (TYPE_DEPOSIT, "Deposit"),
        (TYPE_WITHDRAWAL, "Withdrawal"),
        (TYPE_PHONE_TOPUP, "Phone Top-up"),
        (TYPE_BILL_PAYMENT, "Bill Payment"),
        (TYPE_PURCHASE, "Purchase"),
        (TYPE_GIMTEL, "GIMTEL Transfer"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="sent_transactions",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="received_transactions",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="MRU")
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type} {self.amount} — {self.status}"


def transfer_funds(sender_user, receiver_user, amount, description=""):
    """Atomic transfer between two wallets."""
    if sender_user == receiver_user:
        return False, "You cannot send money to yourself.", None

    if amount <= 0:
        return False, "Amount must be greater than zero.", None

    with transaction.atomic():
        sender_wallet = Wallet.objects.select_for_update().get_or_create(
            user=sender_user, defaults={"balance": 1000.00}
        )[0]
        receiver_wallet = Wallet.objects.select_for_update().get_or_create(
            user=receiver_user, defaults={"balance": 1000.00}
        )[0]

        if not sender_wallet.can_debit(amount):
            return False, f"Insufficient balance. Your balance is {sender_wallet.balance} {sender_wallet.currency}.", None

        sender_wallet.balance -= amount
        sender_wallet.save()
        receiver_wallet.balance += amount
        receiver_wallet.save()

        txn = Transaction.objects.create(
            sender=sender_user,
            receiver=receiver_user,
            amount=amount,
            transaction_type=Transaction.TYPE_TRANSFER,
            status=Transaction.STATUS_SUCCESS,
            description=description,
        )

    return True, f"Successfully sent {amount} MRU to {receiver_user.username}.", txn


def process_payment(user, amount, payment_type, description="", reference=""):
    """Process bill payment, phone topup, purchase, withdrawal."""
    if amount <= 0:
        return False, "Amount must be greater than zero.", None

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get_or_create(
            user=user, defaults={"balance": 1000.00}
        )[0]

        if not wallet.can_debit(amount):
            return False, f"Insufficient balance. Your balance is {wallet.balance} {wallet.currency}.", None

        wallet.balance -= amount
        wallet.save()

        txn = Transaction.objects.create(
            sender=user,
            amount=amount,
            transaction_type=payment_type,
            status=Transaction.STATUS_SUCCESS,
            description=description,
            reference=reference,
        )

    return True, f"Payment of {amount} MRU processed successfully.", txn
