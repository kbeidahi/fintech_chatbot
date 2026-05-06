"""Wallet URL patterns."""
from django.urls import path
from .views import (
    WalletBalanceView, TransactionListView,
    TransferView, PhoneTopupView, BillPaymentView
)

urlpatterns = [
    path('balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('transactions/', TransactionListView.as_view(), name='wallet-transactions'),
    path('transfer/', TransferView.as_view(), name='wallet-transfer'),
    path('topup/', PhoneTopupView.as_view(), name='wallet-topup'),
    path('pay-bill/', BillPaymentView.as_view(), name='wallet-pay-bill'),
]
