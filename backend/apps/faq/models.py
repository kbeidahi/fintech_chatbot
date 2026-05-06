"""FAQ knowledge base — fintech domain."""
from django.db import models


class FAQCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default="help_outline")

    def __str__(self):
        return self.name


class FAQItem(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name="items")
    question = models.TextField()
    answer = models.TextField()
    # Keywords used for intent matching (comma-separated)
    keywords = models.TextField(
        help_text="Comma-separated keywords for matching, e.g. 'transfer,send money,wire'"
    )
    priority = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    def keyword_list(self):
        return [k.strip().lower() for k in self.keywords.split(",") if k.strip()]

    def __str__(self):
        return self.question[:60]


# ── Built-in fintech FAQ data ────────────────────────────────────────────────
# Loaded by management command: python manage.py seed_faq

FINTECH_FAQ = [
    # Account
    {
        "category": "Account",
        "question": "How do I open an account?",
        "answer": (
            "Opening an account is quick and fully digital. Download our app, tap 'Create account', "
            "provide your full name, email, phone number, and a government-issued ID. "
            "Verification takes up to 24 hours. Once approved, your account is ready to use."
        ),
        "keywords": "open account,create account,sign up,register,new account",
    },
    {
        "category": "Account",
        "question": "How do I reset my PIN or password?",
        "answer": (
            "To reset your PIN: go to Settings → Security → Change PIN. "
            "To reset your password: on the login screen tap 'Forgot password', enter your email, "
            "and follow the link we send you. For security, password resets expire after 15 minutes."
        ),
        "keywords": "reset pin,forgot pin,change pin,reset password,forgot password,password",
    },
    {
        "category": "Account",
        "question": "How do I close my account?",
        "answer": (
            "To close your account, ensure your balance is zero and there are no pending transactions. "
            "Then go to Settings → Account → Close account and follow the steps. "
            "Alternatively, contact our support team. Closed accounts cannot be reopened."
        ),
        "keywords": "close account,delete account,cancel account",
    },
    # Transfers
    {
        "category": "Transfers",
        "question": "How do I send money to another person?",
        "answer": (
            "Tap the 'Transfer' button on the home screen. Enter the recipient's phone number, email, "
            "or account number. Type the amount and confirm with your PIN. "
            "Transfers between accounts in our platform are instant and free. "
            "Bank transfers take 1–3 business days."
        ),
        "keywords": "send money,transfer,wire,pay someone,send funds,transfer money",
    },
    {
        "category": "Transfers",
        "question": "What are the transfer limits?",
        "answer": (
            "Default limits: single transfer up to $5,000, daily up to $10,000, monthly up to $50,000. "
            "Verified Premium accounts have higher limits. "
            "Limits may be adjusted based on your account activity and verification level."
        ),
        "keywords": "transfer limit,sending limit,maximum transfer,how much can i send,limit",
    },
    {
        "category": "Transfers",
        "question": "Can I cancel a transfer?",
        "answer": (
            "Transfers between platform accounts are instant and cannot be cancelled. "
            "Bank wire transfers can be cancelled within 30 minutes of initiation — "
            "go to Activity → find the transaction → tap 'Cancel'. "
            "After 30 minutes, contact support immediately."
        ),
        "keywords": "cancel transfer,undo transfer,reverse transfer,stop payment",
    },
    # Cards
    {
        "category": "Cards",
        "question": "How do I order a debit card?",
        "answer": (
            "Go to Cards → Add card → Request physical card. Choose your delivery address. "
            "Cards are mailed within 5–7 business days. "
            "You can use a virtual card instantly while you wait for the physical card."
        ),
        "keywords": "order card,debit card,request card,get card,physical card",
    },
    {
        "category": "Cards",
        "question": "My card was lost or stolen. What do I do?",
        "answer": (
            "Freeze your card immediately: Cards → select your card → Freeze. "
            "Then report it lost or stolen under the same menu — this permanently blocks the card "
            "and orders a replacement automatically. Your replacement arrives in 5–7 business days."
        ),
        "keywords": "lost card,stolen card,block card,freeze card,stolen,lost",
    },
    {
        "category": "Cards",
        "question": "How do I change my card spending limit?",
        "answer": (
            "Go to Cards → select your card → Spending limits. "
            "You can adjust daily ATM, POS, and online spending limits independently. "
            "Changes take effect immediately. Premium accounts can request higher limits via support."
        ),
        "keywords": "card limit,spending limit,atm limit,increase limit,card spending",
    },
    # Fees
    {
        "category": "Fees",
        "question": "What fees does the platform charge?",
        "answer": (
            "Core features are free: account opening, internal transfers, virtual card, basic statements. "
            "Fees apply to: international wire transfers ($15 flat), ATM withdrawals outside network ($2.50), "
            "physical card replacement ($5), expedited transfers (0.5%). "
            "Full fee schedule is available in Settings → Fee schedule."
        ),
        "keywords": "fees,charges,cost,how much,pricing,fee schedule,free",
    },
    # Security
    {
        "category": "Security",
        "question": "Is my money safe?",
        "answer": (
            "Yes. Customer funds are held in FDIC-insured partner banks up to $250,000 per depositor. "
            "We use 256-bit AES encryption, biometric authentication, and real-time fraud monitoring. "
            "We will never ask for your password or PIN via phone, email, or chat."
        ),
        "keywords": "safe,secure,insured,fdic,protection,security,fraud,encryption",
    },
    {
        "category": "Security",
        "question": "I think my account was hacked. What should I do?",
        "answer": (
            "Act immediately: freeze your card and account in the app (Settings → Security → Freeze account). "
            "Change your password using the 'Forgot password' flow. "
            "Contact our fraud team at fraud@fintechapp.com or call the 24/7 hotline: 1-800-000-0000. "
            "We will review all recent transactions and dispute any unauthorized ones."
        ),
        "keywords": "hacked,compromised,unauthorized,fraud,suspicious activity,stolen account",
    },
    # Loans / Credit
    {
        "category": "Loans",
        "question": "How do I apply for a personal loan?",
        "answer": (
            "Go to Products → Loans → Apply. You'll need to provide income details and consent to a soft credit check. "
            "Decisions are usually instant. Loan amounts range from $500 to $50,000 with APRs from 5.9% to 29.9% "
            "depending on your credit profile. Funds are deposited within one business day of approval."
        ),
        "keywords": "loan,personal loan,borrow,credit,apply loan,need money",
    },
    # Support
    {
        "category": "Support",
        "question": "How do I contact customer support?",
        "answer": (
            "You can reach support through: this chat (available 24/7), "
            "email at support@fintechapp.com (response within 4 hours), "
            "or phone at 1-800-000-0000 (Mon–Fri 8 AM–8 PM EST). "
            "For urgent fraud issues, our fraud hotline is available 24/7."
        ),
        "keywords": "contact,support,help,customer service,phone number,email,human",
    },
]
