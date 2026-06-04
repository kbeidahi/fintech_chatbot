"""
Multilingual Intent Engine
Supports: Arabic, French, English
Two-layer pipeline:
  1. ACTION  — detects transactional commands and executes them
  2. INQUIRY — FAQ matching + Gemini for general questions
"""
import logging
import re
import json
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from urllib.parse import quote
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model

from apps.faq.multilingual_faq import MULTILINGUAL_FAQ
from apps.wallet.models import Wallet, transfer_funds, process_payment, Transaction

User = get_user_model()
logger = logging.getLogger(__name__)


# ── Language detection ────────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    arabic_chars = len(re.findall(r'[؀-ۿ]', text))
    french_words = [
        'bonjour', 'salut', 'bonsoir', 'solde', 'virement', 'virer', 'recharge',
        'recharger', 'facture', 'retrait', 'retirer', 'achat', 'payer', 'paiement',
        'comment', 'mon', 'mes', 'je', 'vous', 'nous', 'est', 'les', 'des', 'une',
        'pour', 'faire', 'voir', 'quel', 'quelle', 'combien', 'aide', 'merci',
        'argent', 'compte', 'carte', 'code', 'frais', 'envoyer', 'transférer',
    ]
    text_lower = text.lower()
    if arabic_chars > 2:
        return 'ar'
    if any(re.search(rf'\b{re.escape(w)}\b', text_lower) for w in french_words):
        return 'fr'
    return 'en'


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s؀-ۿ]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# ── Extraction helpers ────────────────────────────────────────────────────────

def extract_amount(text: str) -> Optional[Decimal]:
    match = re.search(r'\b(\d+(?:[.,]\d+)?)\b', text)
    if match:
        try:
            return Decimal(match.group(1).replace(',', '.'))
        except InvalidOperation:
            return None
    return None


def extract_username(text: str) -> Optional[str]:
    patterns = [
        r'(?:to|إلى|à|pour|vers|لـ|ل)\s+(\w+)',
        r'(?:transfer|حول|virer|envoyer)\s+\d+\s+(?:to|إلى|à)\s+(\w+)',
        r'(\w+)$',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group(1)
            if candidate.lower() not in ['to', 'à', 'pour', 'vers', 'إلى', 'لـ']:
                return candidate
    return None


def extract_phone(text: str) -> Optional[str]:
    match = re.search(r'\b(\d{8,12})\b', text)
    return match.group(1) if match else None


def extract_bill_type(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ['كهرباء', 'électricité', 'electricity', 'electric']):
        return 'electricity'
    if any(w in text_lower for w in ['ماء', 'eau', 'water']):
        return 'water'
    if any(w in text_lower for w in ['انترنت', 'internet']):
        return 'internet'
    return 'general'


def extract_gimtel_app(text: str) -> Optional[str]:
    apps = {
        'bankily': ['bankily', 'بنكيلي'],
        'click': ['click', 'كليك'],
        'sedad': ['sedad', 'سيداد'],
        'bamis': ['bamis', 'باميس'],
        'gazapay': ['gaza pay', 'gazapay', 'gaza'],
        'moovmoney': ['moov money', 'moovmoney', 'moov'],
        'masrivi': ['masrivi', 'مصرفي'],
    }
    text_lower = text.lower()
    for app_key, keywords in apps.items():
        if any(k in text_lower for k in keywords):
            return app_key
    return None


# ── Action response templates ─────────────────────────────────────────────────

ACTION_RESPONSES = {
    'balance_result': {
        'ar': '💰 رصيدك الحالي: **{balance} {currency}**',
        'fr': '💰 Votre solde actuel: **{balance} {currency}**',
        'en': '💰 Your current balance: **{balance} {currency}**',
    },
    'transfer_success': {
        'ar': '✅ تم التحويل بنجاح!\n• المبلغ: {amount} MRU\n• إلى: {receiver}\n• رصيدك الجديد: {balance} MRU',
        'fr': '✅ Virement effectué!\n• Montant: {amount} MRU\n• Vers: {receiver}\n• Nouveau solde: {balance} MRU',
        'en': '✅ Transfer successful!\n• Amount: {amount} MRU\n• To: {receiver}\n• New balance: {balance} MRU',
    },
    'transfer_need_info': {
        'ar': 'لتحويل الأموال أرسل:\n**حول [المبلغ] إلى [رقم الهاتف]**\nمثال: حول 500 إلى 22334455',
        'fr': 'Pour virer, tapez:\n**virer [montant] à [numéro]**\nEx: virer 500 à 22334455',
        'en': 'To transfer, type:\n**transfer [amount] to [phone number]**\nEx: transfer 500 to 22334455',
    },
    'topup_success': {
        'ar': '✅ تم الشحن بنجاح!\n• الرقم: {phone}\n• المبلغ: {amount} MRU\n• رصيدك الجديد: {balance} MRU',
        'fr': '✅ Recharge effectuée!\n• Numéro: {phone}\n• Montant: {amount} MRU\n• Nouveau solde: {balance} MRU',
        'en': '✅ Top-up successful!\n• Number: {phone}\n• Amount: {amount} MRU\n• New balance: {balance} MRU',
    },
    'topup_need_info': {
        'ar': 'لشحن الهاتف أرسل:\n**شحن [رقم الهاتف] [المبلغ]**\nمثال: شحن 22334455 100',
        'fr': 'Pour recharger, tapez:\n**recharge [numéro] [montant]**\nEx: recharge 22334455 100',
        'en': 'To top up, type:\n**topup [phone] [amount]**\nEx: topup 22334455 100',
    },
    'bill_success': {
        'ar': '✅ تم دفع الفاتورة!\n• النوع: {type}\n• المبلغ: {amount} MRU\n• رصيدك الجديد: {balance} MRU',
        'fr': '✅ Facture payée!\n• Type: {type}\n• Montant: {amount} MRU\n• Nouveau solde: {balance} MRU',
        'en': '✅ Bill paid!\n• Type: {type}\n• Amount: {amount} MRU\n• New balance: {balance} MRU',
    },
    'bill_need_info': {
        'ar': 'لدفع الفاتورة أرسل:\n**دفع فاتورة [النوع] [المبلغ]**\nمثال: دفع فاتورة كهرباء 500',
        'fr': 'Pour payer, tapez:\n**payer facture [type] [montant]**\nEx: payer facture électricité 500',
        'en': 'To pay a bill, type:\n**pay bill [type] [amount]**\nEx: pay bill electricity 500',
    },
    'withdrawal_success': {
        'ar': '✅ تم السحب بنجاح!\n• المبلغ: {amount} MRU\n• رصيدك الجديد: {balance} MRU\n📍 استلم النقود من أقرب وكالة.',
        'fr': '✅ Retrait effectué!\n• Montant: {amount} MRU\n• Nouveau solde: {balance} MRU\n📍 Récupérez l\'argent à l\'agence la plus proche.',
        'en': '✅ Withdrawal successful!\n• Amount: {amount} MRU\n• New balance: {balance} MRU\n📍 Collect cash from the nearest agency.',
    },
    'gimtel_success': {
        'ar': '✅ تم التحويل عبر GIMTEL!\n• إلى: {app}\n• المبلغ: {amount} MRU\n• رصيدك الجديد: {balance} MRU',
        'fr': '✅ Virement GIMTEL effectué!\n• Vers: {app}\n• Montant: {amount} MRU\n• Nouveau solde: {balance} MRU',
        'en': '✅ GIMTEL transfer done!\n• To: {app}\n• Amount: {amount} MRU\n• New balance: {balance} MRU',
    },
    'insufficient_balance': {
        'ar': '❌ رصيد غير كافٍ\n• رصيدك الحالي: {balance} MRU',
        'fr': '❌ Solde insuffisant\n• Votre solde: {balance} MRU',
        'en': '❌ Insufficient balance\n• Your balance: {balance} MRU',
    },
    'user_not_found': {
        'ar': '❌ لا يوجد حساب برقم الهاتف **{username}**.\nتحقق من الرقم وحاول مرة أخرى.',
        'fr': '❌ Aucun compte avec le numéro **{username}**.\nVérifiez le numéro et réessayez.',
        'en': '❌ No account found with phone number **{username}**.\nCheck the number and try again.',
    },
}


def action_response(key: str, lang: str, **kwargs) -> str:
    tpl = ACTION_RESPONSES.get(key, {}).get(lang) or ACTION_RESPONSES.get(key, {}).get('en', '')
    try:
        return tpl.format(**kwargs)
    except KeyError:
        return tpl


# ── Unknown / fallback ────────────────────────────────────────────────────────

UNKNOWN_RESPONSE = {
    'ar': (
        'عذراً، لم أفهم سؤالك تماماً 🤔\n\n'
        'يمكنني مساعدتك في:\n'
        '💰 رصيد  📱 شحن  💸 تحويل\n'
        '🔄 GIMTEL  🧾 فواتير  💵 سحب\n\n'
        'حاول إعادة صياغة سؤالك!'
    ),
    'fr': (
        'Désolé, je n\'ai pas compris 🤔\n\n'
        'Je peux vous aider avec:\n'
        '💰 Solde  📱 Recharge  💸 Virement\n'
        '🔄 GIMTEL  🧾 Factures  💵 Retrait\n\n'
        'Reformulez votre question!'
    ),
    'en': (
        'Sorry, I didn\'t understand 🤔\n\n'
        'I can help with:\n'
        '💰 Balance  📱 Top-up  💸 Transfer\n'
        '🔄 GIMTEL  🧾 Bills  💵 Withdrawal\n\n'
        'Try rephrasing your question!'
    ),
}


# ── LLM system prompts ────────────────────────────────────────────────────────

_APP_KNOWLEDGE = """
APP SERVICES YOU KNOW ABOUT:
1. Balance: User can check their real-time wallet balance anytime from the home screen.
2. Transfer: Send money to another user by phone number. Requires PIN confirmation.
3. Phone Top-up (Recharge): Recharge Mauritel, Chinguitel, or Mattel. Requires phone number, amount, and PIN.
4. Bill Payment: Pay electricity, water, internet, TV (TOD/BeIN), insurance, education, air transport bills. Requires customer ID and PIN.
5. Cash Withdrawal: Generate a withdrawal code via the app, go to an agency, give the code to the agent. Requires PIN.
6. B-Pay: Pay merchants by entering their merchant ID and amount. Requires PIN.
7. GIMTEL: Transfer money to other fintech apps (Bankily, Click, Sedad, Masrivi, Moov Money, Bamis). Requires PIN.
8. Debit Card: Request a new card, view details, freeze/unfreeze, set spending limits.
9. Cheque Book: Request a cheque book from the Accounts section.
10. PIN: 4-digit secret code required for all financial operations. Can be changed in Settings > Security.

IMPORTANT RULES:
- You CANNOT execute transactions yourself. For actual actions (transfer money, pay bills, etc.), tell the user to use the Wallet tab or type the command.
- You CAN explain how everything works, guide the user step by step, answer any question.
- Always be helpful, warm, and use emojis naturally.
- Keep casual replies short. Give detailed step-by-step for technical questions.
- If the user seems confused, ask a clarifying question.
- Match the user's language and tone.
"""

# ── Gemini classification prompt ─────────────────────────────────────────────

GEMINI_CLASSIFIER_PROMPT = """
You are an intent classifier for FinAssist, a fintech app assistant.
Read the user message and return ONLY a valid JSON object — no markdown, no explanation.

JSON format:
{
  "type": "action" | "inquiry" | "social" | "general",
  "intent": "<intent>",
  "params": {},
  "lang": "ar" | "fr" | "en"
}

TYPE definitions:
- "action"  : user wants to EXECUTE a financial operation right now
- "inquiry" : user wants to LEARN / understand how something works
- "social"  : greeting, thanks, goodbye, feelings, small talk
- "general" : any other question not covered above

INTENTS:
  action intents  : balance_check, transfer, topup, bill_payment, withdrawal, gimtel, bpay
  inquiry intents : balance_info, transfer_info, topup_info, bill_info, withdrawal_info,
                    gimtel_info, bpay_info, card_info, cheque_info, pin_info
  social intents  : greeting, thanks, goodbye, how_are_you, compliment, apology,
                    feeling_good, feeling_bad, who_are_you, what_can_you_do, help_request, other_social
  general intent  : general_question

PARAMS to extract (only for action type):
  transfer      : {"amount": <number>, "recipient": "<phone_number>"}
  topup         : {"amount": <number>, "phone": "<phone_number>"}
  bill_payment  : {"amount": <number>, "bill_type": "<type>", "reference": "<id>"}
  withdrawal    : {"amount": <number>}
  gimtel        : {"amount": <number>, "app": "<app_name>"}
  bpay          : {"amount": <number>, "merchant_id": "<id>"}
  balance_check : {}

LANG: detect from the user message (ar=Arabic, fr=French, en=English)

EXAMPLES:
"transfer 500 to 22334455"        → {"type":"action","intent":"transfer","params":{"amount":500,"recipient":"22334455"},"lang":"en"}
"I want to send money to my friend" → {"type":"action","intent":"transfer","params":{},"lang":"en"}
"how do I transfer money?"        → {"type":"inquiry","intent":"transfer_info","params":{},"lang":"en"}
"what's my balance?"              → {"type":"action","intent":"balance_check","params":{},"lang":"en"}
"how can I check my balance?"     → {"type":"inquiry","intent":"balance_info","params":{},"lang":"en"}
"حول 500 إلى 22334455"            → {"type":"action","intent":"transfer","params":{"amount":500,"recipient":"22334455"},"lang":"ar"}
"كيف أحول الأموال؟"               → {"type":"inquiry","intent":"transfer_info","params":{},"lang":"ar"}
"اشحن هاتف 22334455 بـ 100"       → {"type":"action","intent":"topup","params":{"amount":100,"phone":"22334455"},"lang":"ar"}
"comment faire un virement?"      → {"type":"inquiry","intent":"transfer_info","params":{},"lang":"fr"}
"virer 500 à 22334455"            → {"type":"action","intent":"transfer","params":{"amount":500,"recipient":"22334455"},"lang":"fr"}
"merci"                           → {"type":"social","intent":"thanks","params":{},"lang":"fr"}
"bonjour"                         → {"type":"social","intent":"greeting","params":{},"lang":"fr"}
"what is bitcoin?"                → {"type":"general","intent":"general_question","params":{},"lang":"en"}
""".strip()


# ── General chat prompt (used when type=general) ──────────────────────────────

LLM_SYSTEM_PROMPTS = {
    'ar': (
        'أنت FinAssist، مساعد مالي ذكي وودود. شخصيتك دافئة وتستخدم إيموجي بشكل طبيعي. '
        'أجب على أي سؤال عام بطريقة مفيدة وذكية. أجب بالعربية.'
    ),
    'fr': (
        'Vous êtes FinAssist, un assistant financier intelligent et chaleureux. '
        'Répondez à toute question générale de façon utile et intelligente. Répondez en français.'
    ),
    'en': (
        'You are FinAssist, a smart and friendly financial assistant. '
        'Answer any general question in a helpful and clever way. Reply in English.'
    ),
}


# ── Gemini classify (Layer 1 — intent understanding) ─────────────────────────

def gemini_classify(user_message: str) -> Optional[dict]:
    """Send message to Gemini for intent classification. Returns dict or None."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash').strip()
    model_path = model if model.startswith('models/') else f'models/{model}'

    body = json.dumps({
        'system_instruction': {'parts': [{'text': GEMINI_CLASSIFIER_PROMPT}]},
        'contents': [{'role': 'user', 'parts': [{'text': user_message}]}],
        'generationConfig': {'temperature': 0.1, 'maxOutputTokens': 256},
    }).encode('utf-8')

    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/{quote(model_path, safe="/")}:generateContent?key={api_key}',
        data=body, headers={'Content-Type': 'application/json'}, method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode('utf-8'))

    candidates = data.get('candidates') or []
    if not candidates:
        return None
    parts = candidates[0].get('content', {}).get('parts') or []
    raw = ''.join(part.get('text', '') for part in parts).strip()

    # Strip markdown code fences if present
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw).strip()

    return json.loads(raw)


# ── Gemini general chat (used when type=general) ──────────────────────────────

def gemini_fallback(user_message: str, lang: str) -> str:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return ''
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash').strip()
    model_path = model if model.startswith('models/') else f'models/{model}'

    body = json.dumps({
        'system_instruction': {
            'parts': [{'text': LLM_SYSTEM_PROMPTS.get(lang, LLM_SYSTEM_PROMPTS['en'])}],
        },
        'contents': [{'role': 'user', 'parts': [{'text': user_message}]}],
        'generationConfig': {'temperature': 0.3, 'maxOutputTokens': 1024},
    }).encode('utf-8')

    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/{quote(model_path, safe="/")}:generateContent?key={api_key}',
        data=body, headers={'Content-Type': 'application/json'}, method='POST',
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.loads(response.read().decode('utf-8'))

    candidates = data.get('candidates') or []
    if not candidates:
        return ''
    parts = candidates[0].get('content', {}).get('parts') or []
    return ''.join(part.get('text', '') for part in parts).strip()


# ── FAQ matching ──────────────────────────────────────────────────────────────

CONFIDENCE_THRESHOLD = 0.01


def _match_faq(norm_text: str, lang: str):
    best_score = 0.0
    best_item = None
    for item in MULTILINGUAL_FAQ:
        keywords_key = f'keywords_{lang}'
        if keywords_key not in item:
            keywords_key = 'keywords_en'
        keywords = [k.strip().lower() for k in item.get(keywords_key, '').split(',')]
        score = 0.0
        for kw in keywords:
            if kw and kw in norm_text:
                score = max(score, 0.70 if ' ' in kw else 0.45)
            elif kw:
                words = norm_text.split()
                best = max((similarity(w, kw) for w in words), default=0)
                if best >= 0.85:
                    score = max(score, best * 0.45)
        q_key = f'question_{lang}'
        if q_key in item:
            q_sim = similarity(norm_text, normalize(item[q_key]))
            if q_sim >= 0.72:
                score = max(score, q_sim * 0.9)
        if score > best_score:
            best_score = score
            best_item = item
    return best_item, best_score


# ── Action keyword detection (must include amount to be an action) ─────────────

ACTION_KEYWORDS = {
    'balance': {
        'ar': ['رصيد', 'رصيدي', 'كم عندي', 'اعرض رصيد', 'شوف رصيد'],
        'fr': ['solde', 'mon solde', 'voir solde', 'afficher solde'],
        'en': ['balance', 'my balance', 'show balance', 'check balance'],
    },
    'transfer': {
        'ar': ['حول', 'تحويل', 'ارسل', 'أرسل', 'بعث'],
        'fr': ['virer', 'virement', 'transférer', 'envoyer'],
        'en': ['transfer', 'send money', 'send'],
    },
    'topup': {
        'ar': ['شحن', 'اشحن', 'تعبئة'],
        'fr': ['recharge', 'recharger'],
        'en': ['topup', 'top up', 'recharge'],
    },
    'bill': {
        'ar': ['دفع فاتورة', 'سداد فاتورة', 'تسديد فاتورة'],
        'fr': ['payer facture', 'régler facture', 'paiement facture'],
        'en': ['pay bill', 'pay electricity', 'pay water', 'pay internet'],
    },
    'withdrawal': {
        'ar': ['سحب', 'أسحب', 'اسحب'],
        'fr': ['retrait', 'retirer'],
        'en': ['withdraw', 'cash out'],
    },
    'gimtel': {
        'ar': ['جيمتل', 'بنكيلي', 'كليك', 'سيداد', 'باميس'],
        'fr': ['gimtel', 'bankily', 'click', 'sedad', 'bamis'],
        'en': ['gimtel', 'bankily', 'click', 'sedad', 'bamis'],
    },
}


_INQUIRY_WORDS = [
    # English
    'how', 'what', 'why', 'where', 'when', 'can i', 'do i', 'should i',
    'how do', 'how can', 'how to', 'how does', 'is it', 'tell me',
    # French
    'comment', 'pourquoi', 'qu est', 'quel', 'quelle', 'où', 'est ce',
    'comment faire', 'comment puis', 'expliquer', 'expliquez',
    # Arabic
    'كيف', 'ماذا', 'ما هو', 'ما هي', 'أين', 'متى', 'لماذا',
    'كيف أ', 'كيف يمكن', 'اشرح', 'وضح', 'ممكن تشرح',
]


def _is_inquiry(norm: str) -> bool:
    """Return True if the message is a question/inquiry rather than a command."""
    return any(word in norm for word in _INQUIRY_WORDS)


def detect_action(norm: str, lang: str) -> Optional[str]:
    """
    Returns the action type only if the message looks like a COMMAND
    (contains action keyword + typically an amount or target).
    Simple inquiry questions like 'how do I transfer?' won't match.
    """
    # Inquiry phrasing overrides action detection for all types
    if _is_inquiry(norm):
        return None

    for action, lang_kws in ACTION_KEYWORDS.items():
        kws = lang_kws.get(lang, [])
        for kw in kws:
            if kw in norm:
                # Balance is special — no amount needed
                if action == 'balance':
                    return action
                # For all others, require a number (amount) in the message
                if re.search(r'\b\d+\b', norm):
                    return action
    return None


# ── Inquiry answers (returned when Gemini classifies type=inquiry) ────────────

INQUIRY_ANSWERS = {
    'balance_info': {
        'ar': '💰 لمعرفة رصيدك:\n\n1️⃣ افتح التطبيق\n2️⃣ اضغط على تبويب "المحفظة" في أسفل الشاشة\n3️⃣ سيظهر رصيدك فوراً\n\n✅ الرصيد يتحدث تلقائياً مع كل معاملة.',
        'fr': '💰 Pour consulter votre solde:\n\n1️⃣ Ouvrez l\'application\n2️⃣ Appuyez sur l\'onglet "Portefeuille"\n3️⃣ Votre solde s\'affiche immédiatement\n\n✅ Le solde se met à jour en temps réel.',
        'en': '💰 To check your balance:\n\n1️⃣ Open the app\n2️⃣ Tap the "Wallet" tab at the bottom\n3️⃣ Your balance appears instantly\n\n✅ Balance updates in real-time with every transaction.',
    },
    'transfer_info': {
        'ar': '💸 لتحويل الأموال:\n\n1️⃣ اضغط على "تحويل" في المحفظة\n2️⃣ أدخل رقم هاتف المستلم\n3️⃣ أدخل المبلغ\n4️⃣ أدخل رقمك السري للتأكيد\n\n✅ التحويل فوري!\n⚠️ تحقق من رقم المستلم قبل التأكيد.',
        'fr': '💸 Pour faire un virement:\n\n1️⃣ Appuyez sur "Virement" dans le Portefeuille\n2️⃣ Entrez le numéro de téléphone du destinataire\n3️⃣ Entrez le montant\n4️⃣ Confirmez avec votre code PIN\n\n✅ Virement instantané!\n⚠️ Vérifiez bien le numéro avant de confirmer.',
        'en': '💸 To transfer money:\n\n1️⃣ Tap "Transfer" in the Wallet\n2️⃣ Enter the recipient\'s phone number\n3️⃣ Enter the amount\n4️⃣ Confirm with your PIN\n\n✅ Transfer is instant!\n⚠️ Double-check the phone number before confirming.',
    },
    'topup_info': {
        'ar': '📱 لشحن الهاتف:\n\n1️⃣ اضغط على "شحن" في المحفظة\n2️⃣ اختر الشبكة (موريتل / شنقيتل / ماتل)\n3️⃣ أدخل رقم الهاتف\n4️⃣ أدخل المبلغ\n5️⃣ أكّد بالرقم السري\n\n✅ الشحن فوري!',
        'fr': '📱 Pour recharger un téléphone:\n\n1️⃣ Appuyez sur "Recharge" dans le Portefeuille\n2️⃣ Choisissez le réseau (Mauritel / Chinguitel / Mattel)\n3️⃣ Entrez le numéro\n4️⃣ Entrez le montant\n5️⃣ Confirmez avec le PIN\n\n✅ Recharge instantanée!',
        'en': '📱 To top up a phone:\n\n1️⃣ Tap "Top-up" in the Wallet\n2️⃣ Choose the network (Mauritel / Chinguitel / Mattel)\n3️⃣ Enter the phone number\n4️⃣ Enter the amount\n5️⃣ Confirm with your PIN\n\n✅ Top-up is instant!',
    },
    'bill_info': {
        'ar': '🧾 لدفع الفواتير:\n\n1️⃣ اضغط على "فاتورة" في المحفظة\n2️⃣ اختر نوع الفاتورة (كهرباء، ماء، إنترنت...)\n3️⃣ أدخل معرّفك (ID)\n4️⃣ ستظهر تفاصيل الفاتورة\n5️⃣ أكّد بالرقم السري\n\n✅ الدفع فوري!',
        'fr': '🧾 Pour payer une facture:\n\n1️⃣ Appuyez sur "Facture" dans le Portefeuille\n2️⃣ Choisissez le type (Électricité, Eau, Internet...)\n3️⃣ Entrez votre identifiant client\n4️⃣ Les détails s\'affichent\n5️⃣ Confirmez avec le PIN\n\n✅ Paiement instantané!',
        'en': '🧾 To pay a bill:\n\n1️⃣ Tap "Bill" in the Wallet\n2️⃣ Choose the type (Electricity, Water, Internet...)\n3️⃣ Enter your customer ID\n4️⃣ Bill details will appear\n5️⃣ Confirm with your PIN\n\n✅ Payment is instant!',
    },
    'withdrawal_info': {
        'ar': '💵 لسحب الأموال نقداً:\n\n1️⃣ اضغط "Cash out" في التطبيق\n2️⃣ أدخل رقم الوكالة\n3️⃣ أدخل المبلغ\n4️⃣ أكّد بالرقم السري\n5️⃣ ستصلك رسالة SMS بكود السحب\n6️⃣ أعطِ الكود لصاحب الوكالة\n\n⚠️ لا تشارك الكود مع أي شخص غير الوكيل.',
        'fr': '💵 Pour retirer de l\'argent:\n\n1️⃣ Appuyez "Cash out" dans l\'app\n2️⃣ Entrez le numéro de l\'agence\n3️⃣ Entrez le montant\n4️⃣ Confirmez avec le PIN\n5️⃣ Vous recevrez un code par SMS\n6️⃣ Donnez le code à l\'agent\n\n⚠️ Ne partagez le code qu\'avec l\'agent.',
        'en': '💵 To withdraw cash:\n\n1️⃣ Tap "Cash out" in the app\n2️⃣ Enter the agency number\n3️⃣ Enter the amount\n4️⃣ Confirm with your PIN\n5️⃣ You\'ll receive a withdrawal code by SMS\n6️⃣ Give the code to the agent\n\n⚠️ Only share the code with the agency.',
    },
    'gimtel_info': {
        'ar': '🔄 لإرسال المال عبر GIMTEL:\n\n1️⃣ اضغط على أيقونة "GIMTEL" في المحفظة\n2️⃣ اختر التطبيق المستلم (بنكيلي، كليك، سيداد...)\n3️⃣ أدخل رقم هاتف المستلم\n4️⃣ أدخل المبلغ\n5️⃣ أكّد بالرقم السري\n\n✅ التحويل فوري!',
        'fr': '🔄 Pour envoyer via GIMTEL:\n\n1️⃣ Appuyez sur l\'icône "GIMTEL"\n2️⃣ Choisissez l\'app destinataire (Bankily, Click, Sedad...)\n3️⃣ Entrez le numéro du destinataire\n4️⃣ Entrez le montant\n5️⃣ Confirmez avec le PIN\n\n✅ Transfert instantané!',
        'en': '🔄 To send money via GIMTEL:\n\n1️⃣ Tap the "GIMTEL" icon in the Wallet\n2️⃣ Choose the target app (Bankily, Click, Sedad...)\n3️⃣ Enter recipient\'s phone number\n4️⃣ Enter the amount\n5️⃣ Confirm with your PIN\n\n✅ Transfer is instant!',
    },
    'bpay_info': {
        'ar': '🏪 للدفع عند التجار (B-Pay):\n\n1️⃣ اضغط على "B-Pay" في المحفظة\n2️⃣ أدخل معرّف التاجر\n3️⃣ أدخل المبلغ\n4️⃣ أكّد بالرقم السري\n\n✅ الدفع يصل للتاجر فوراً!',
        'fr': '🏪 Pour payer un marchand (B-Pay):\n\n1️⃣ Appuyez sur "B-Pay" dans le Portefeuille\n2️⃣ Entrez l\'identifiant du marchand\n3️⃣ Entrez le montant\n4️⃣ Confirmez avec le PIN\n\n✅ Paiement envoyé instantanément!',
        'en': '🏪 To pay a merchant (B-Pay):\n\n1️⃣ Tap "B-Pay" in the Wallet\n2️⃣ Enter the merchant ID\n3️⃣ Enter the amount\n4️⃣ Confirm with your PIN\n\n✅ Payment sent instantly!',
    },
    'card_info': {
        'ar': '💳 خدمات بطاقة الخصم:\n\n• طلب بطاقة جديدة\n• عرض تفاصيل البطاقة\n• تجميد / إلغاء تجميد البطاقة\n• تحديد حدود الإنفاق\n\nمن الصفحة الرئيسية → "بطاقة الخصم"\n\n✅ البطاقة الافتراضية متاحة فوراً.',
        'fr': '💳 Services carte de débit:\n\n• Demander une nouvelle carte\n• Voir les détails\n• Geler / dégeler la carte\n• Définir les limites\n\nAccueil → "Carte débit"\n\n✅ Carte virtuelle disponible immédiatement.',
        'en': '💳 Debit card services:\n\n• Request a new card\n• View card details\n• Freeze / unfreeze the card\n• Set spending limits\n\nHome → "Debit Card"\n\n✅ Virtual card available immediately.',
    },
    'cheque_info': {
        'ar': '📒 لطلب دفتر شيكات:\n\n1️⃣ الصفحة الرئيسية → "الحسابات"\n2️⃣ "طلب دفتر شيكات"\n3️⃣ اختر حسابك وأكّد\n\n✅ جاهز خلال 3-5 أيام عمل.',
        'fr': '📒 Pour demander un chéquier:\n\n1️⃣ Accueil → "Comptes"\n2️⃣ "Demande de chéquier"\n3️⃣ Choisissez votre compte et confirmez\n\n✅ Prêt dans 3 à 5 jours ouvrables.',
        'en': '📒 To request a cheque book:\n\n1️⃣ Home → "Accounts"\n2️⃣ "Request Cheque Book"\n3️⃣ Choose your account and confirm\n\n✅ Ready within 3–5 business days.',
    },
    'pin_info': {
        'ar': '🔑 عن الرقم السري:\n\n• مطلوب لجميع العمليات المالية\n• لا تشاركه مع أحد أبداً\n\nلتغييره:\nالإعدادات ← الأمان ← "تغيير الرقم السري"\n\nنسيت رقمك؟\nشاشة الدخول ← "نسيت كلمة المرور" ← أدخل بريدك الإلكتروني\n\n⚠️ لن نطلب منك رقمك السري أبداً.',
        'fr': '🔑 À propos du code PIN:\n\n• Requis pour toutes les opérations\n• Ne le partagez jamais\n\nPour le changer:\nParamètres → Sécurité → "Changer le PIN"\n\nPIN oublié?\nÉcran connexion → "Mot de passe oublié" → email\n\n⚠️ Nous ne vous demanderons JAMAIS votre PIN.',
        'en': '🔑 About your PIN:\n\n• Required for all financial operations\n• Never share it with anyone\n\nTo change it:\nSettings → Security → "Change PIN"\n\nForgot your PIN?\nLogin screen → "Forgot password" → enter your email\n\n⚠️ We will NEVER ask for your PIN.',
    },
}


# ── Main engine ───────────────────────────────────────────────────────────────

class MultilingualIntentEngine:

    # PIN error responses
    _PIN_REQUIRED = {
        'ar': '🔐 يرجى إدخال رقمك السري (4 أرقام) لتأكيد هذه العملية.',
        'fr': '🔐 Veuillez saisir votre code PIN (4 chiffres) pour confirmer cette opération.',
        'en': '🔐 Please enter your 4-digit PIN to confirm this operation.',
    }
    _PIN_NOT_SET = {
        'ar': '⚠️ لم تقم بتعيين رقم سري بعد. يرجى إعداد الرقم السري من إعدادات الحساب أولاً.',
        'fr': '⚠️ Vous n\'avez pas encore défini de code PIN. Veuillez le configurer dans les paramètres du compte.',
        'en': '⚠️ You have not set a PIN yet. Please set up your PIN in account settings first.',
    }
    _PIN_WRONG = {
        'ar': '❌ رقم سري غير صحيح. يرجى المحاولة مرة أخرى.',
        'fr': '❌ Code PIN incorrect. Veuillez réessayer.',
        'en': '❌ Incorrect PIN. Please try again.',
    }

    def _execute_classified(self, intent: str, params: dict, user, pin: str, lang: str, norm: str) -> dict:
        """Execute an action based on Gemini-classified intent + extracted params."""

        if intent == 'balance_check':
            wallet = Wallet.get_or_create_for_user(user)
            return {'answer': action_response('balance_result', lang, balance=wallet.balance, currency=wallet.currency),
                    'intent': 'check_balance', 'action': 'balance', 'lang': lang, 'source': 'action'}

        # All other actions need PIN
        err = self._check_pin(user, pin, lang)
        if err:
            return err

        amount = params.get('amount')
        if amount:
            try:
                amount = Decimal(str(amount))
            except (InvalidOperation, TypeError):
                amount = None
        # If amount missing, try to extract from original text
        if not amount:
            amount = extract_amount(norm)

        if intent == 'transfer':
            recipient = params.get('recipient') or extract_phone(norm)
            if not recipient or not amount:
                return {'answer': action_response('transfer_need_info', lang),
                        'intent': 'transfer_info', 'lang': lang, 'source': 'action_guide'}
            try:
                User = get_user_model()
                receiver = User.objects.get(phone=recipient)
            except Exception:
                return {'answer': action_response('user_not_found', lang, username=recipient),
                        'intent': 'transfer_failed', 'lang': lang, 'source': 'action'}
            success, msg, txn = transfer_funds(user, receiver, amount)
            wallet = Wallet.get_or_create_for_user(user)
            if success:
                return {'answer': action_response('transfer_success', lang, amount=amount, username=recipient, balance=wallet.balance),
                        'intent': 'transfer', 'action': 'transfer', 'lang': lang, 'source': 'action'}
            return {'answer': action_response('insufficient_balance', lang, balance=wallet.balance),
                    'intent': 'transfer_failed', 'lang': lang, 'source': 'action'}

        if intent == 'topup':
            phone = params.get('phone') or extract_phone(norm)
            if not phone or not amount:
                return {'answer': action_response('topup_need_info', lang),
                        'intent': 'topup_info', 'lang': lang, 'source': 'action_guide'}
            success, msg, _ = process_payment(user, amount, Transaction.TYPE_PHONE_TOPUP, description=f'Phone top-up: {phone}', reference=phone)
            wallet = Wallet.get_or_create_for_user(user)
            if success:
                return {'answer': action_response('topup_success', lang, phone=phone, amount=amount, balance=wallet.balance),
                        'intent': 'phone_topup', 'action': 'topup', 'lang': lang, 'source': 'action'}
            return {'answer': action_response('insufficient_balance', lang, balance=wallet.balance),
                    'intent': 'topup_failed', 'lang': lang, 'source': 'action'}

        if intent == 'bill_payment':
            bill_type = params.get('bill_type', 'general')
            reference = params.get('reference', '')
            if not amount:
                return {'answer': action_response('bill_need_info', lang),
                        'intent': 'bill_info', 'lang': lang, 'source': 'action_guide'}
            success, msg, _ = process_payment(user, amount, Transaction.TYPE_BILL_PAYMENT, description=f'Bill: {bill_type}', reference=reference)
            wallet = Wallet.get_or_create_for_user(user)
            if success:
                return {'answer': action_response('bill_success', lang, bill_type=bill_type, amount=amount, balance=wallet.balance),
                        'intent': 'bill_payment', 'action': 'bill', 'lang': lang, 'source': 'action'}
            return {'answer': action_response('insufficient_balance', lang, balance=wallet.balance),
                    'intent': 'bill_failed', 'lang': lang, 'source': 'action'}

        if intent == 'withdrawal':
            if not amount:
                return {'answer': action_response('withdrawal_need_info', lang),
                        'intent': 'withdrawal_info', 'lang': lang, 'source': 'action_guide'}
            success, msg, _ = process_payment(user, amount, Transaction.TYPE_WITHDRAWAL, description='Cash withdrawal')
            wallet = Wallet.get_or_create_for_user(user)
            if success:
                return {'answer': action_response('withdrawal_success', lang, amount=amount, balance=wallet.balance),
                        'intent': 'withdrawal', 'action': 'withdrawal', 'lang': lang, 'source': 'action'}
            return {'answer': action_response('insufficient_balance', lang, balance=wallet.balance),
                    'intent': 'withdrawal_failed', 'lang': lang, 'source': 'action'}

        if intent == 'gimtel':
            app_name = params.get('app') or extract_app_name(norm)
            if not app_name or not amount:
                return {'answer': action_response('gimtel_need_info', lang),
                        'intent': 'gimtel_info', 'lang': lang, 'source': 'action_guide'}
            success, msg, _ = process_payment(user, amount, Transaction.TYPE_GIMTEL, description=f'GIMTEL to {app_name}')
            wallet = Wallet.get_or_create_for_user(user)
            if success:
                return {'answer': action_response('gimtel_success', lang, app=app_name, amount=amount, balance=wallet.balance),
                        'intent': 'gimtel', 'action': 'gimtel', 'lang': lang, 'source': 'action'}
            return {'answer': action_response('insufficient_balance', lang, balance=wallet.balance),
                    'intent': 'gimtel_failed', 'lang': lang, 'source': 'action'}

        # Unknown action — guide to wallet tab
        return {'answer': INQUIRY_ANSWERS.get(f'{intent}_info', {}).get(lang, UNKNOWN_RESPONSE.get(lang, '')),
                'intent': intent, 'lang': lang, 'source': 'faq'}

    def _check_pin(self, user, pin: str, lang: str) -> dict | None:
        """Returns an error dict if PIN check fails, else None (meaning OK)."""
        if not user.has_pin:
            return {'answer': self._PIN_NOT_SET.get(lang, self._PIN_NOT_SET['en']),
                    'intent': 'pin_not_set', 'lang': lang, 'source': 'pin_error'}
        if not pin:
            return {'answer': self._PIN_REQUIRED.get(lang, self._PIN_REQUIRED['en']),
                    'intent': 'pin_required', 'lang': lang, 'source': 'pin_required'}
        if not user.check_pin(pin):
            return {'answer': self._PIN_WRONG.get(lang, self._PIN_WRONG['en']),
                    'intent': 'pin_wrong', 'lang': lang, 'source': 'pin_error'}
        return None

    def resolve(self, message: str, user=None, pin: str = '') -> dict:
        lang = detect_language(message)
        norm = normalize(message)

        # ════════════════════════════════════════════════════════════════════
        # LAYER 0 — SOCIAL / COURTESY (instant, no API call)
        # ════════════════════════════════════════════════════════════════════
        social = _match_social(norm, lang)
        if social:
            return {'answer': social, 'intent': 'social', 'lang': lang, 'source': 'faq'}

        # ════════════════════════════════════════════════════════════════════
        # LAYER 1 — GEMINI CLASSIFIER (understands intent from any phrasing)
        # ════════════════════════════════════════════════════════════════════
        if settings.GEMINI_API_KEY:
            try:
                classified = gemini_classify(message)
                if classified:
                    lang = classified.get('lang', lang)
                    intent_type = classified.get('type', '')
                    intent = classified.get('intent', '')
                    params = classified.get('params') or {}

                    # ── inquiry → return the predefined FAQ answer ──────────
                    if intent_type == 'inquiry':
                        answer = INQUIRY_ANSWERS.get(intent, {}).get(lang) \
                              or INQUIRY_ANSWERS.get(intent, {}).get('en', '')
                        if answer:
                            return {'answer': answer, 'intent': intent,
                                    'lang': lang, 'source': 'faq'}

                    # ── action → execute via existing action engine ─────────
                    elif intent_type == 'action' and user:
                        return self._execute_classified(intent, params, user, pin, lang, norm)

                    # ── general → full Gemini conversational answer ─────────
                    elif intent_type in ('general', 'social'):
                        answer = gemini_fallback(message, lang)
                        if answer:
                            return {'answer': answer, 'intent': intent,
                                    'lang': lang, 'source': 'gemini'}

            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                    KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
                logger.warning('Gemini classify failed, falling back: %s', exc)

        # ════════════════════════════════════════════════════════════════════
        # LAYER 2 — FALLBACK: old keyword-based action detection
        # ════════════════════════════════════════════════════════════════════
        if user:
            action = detect_action(norm, lang)

            if action == 'balance':
                wallet = Wallet.get_or_create_for_user(user)
                return {
                    'answer': action_response('balance_result', lang,
                                              balance=wallet.balance, currency=wallet.currency),
                    'intent': 'check_balance', 'action': 'balance',
                    'lang': lang, 'source': 'action',
                }

            elif action == 'transfer':
                err = self._check_pin(user, pin, lang)
                if err: return err
                amount = extract_amount(message)
                username = extract_phone(message)
                if amount and username:
                    try:
                        receiver = User.objects.get(phone=username)
                        success, msg, txn = transfer_funds(user, receiver, amount)
                        wallet = Wallet.get_or_create_for_user(user)
                        if success:
                            return {
                                'answer': action_response('transfer_success', lang,
                                                          amount=amount, receiver=username,
                                                          balance=wallet.balance),
                                'intent': 'transfer', 'action': 'transfer',
                                'lang': lang, 'source': 'action',
                            }
                        else:
                            return {
                                'answer': action_response('insufficient_balance', lang,
                                                          balance=wallet.balance),
                                'intent': 'transfer_failed', 'lang': lang, 'source': 'action',
                            }
                    except User.DoesNotExist:
                        return {
                            'answer': action_response('user_not_found', lang, username=username),
                            'intent': 'transfer_failed', 'lang': lang, 'source': 'action',
                        }
                else:
                    return {
                        'answer': action_response('transfer_need_info', lang),
                        'intent': 'transfer_info', 'lang': lang, 'source': 'action_guide',
                    }

            elif action == 'topup':
                err = self._check_pin(user, pin, lang)
                if err: return err
                amount = extract_amount(message)
                phone = extract_phone(message)
                if amount and phone:
                    success, msg, txn = process_payment(
                        user, amount, Transaction.TYPE_PHONE_TOPUP,
                        description=f"Phone top-up: {phone}")
                    wallet = Wallet.get_or_create_for_user(user)
                    if success:
                        return {
                            'answer': action_response('topup_success', lang,
                                                      phone=phone, amount=amount,
                                                      balance=wallet.balance),
                            'intent': 'phone_topup', 'action': 'topup',
                            'lang': lang, 'source': 'action',
                        }
                    else:
                        return {
                            'answer': action_response('insufficient_balance', lang,
                                                      balance=wallet.balance),
                            'intent': 'topup_failed', 'lang': lang, 'source': 'action',
                        }
                else:
                    return {
                        'answer': action_response('topup_need_info', lang),
                        'intent': 'topup_info', 'lang': lang, 'source': 'action_guide',
                    }

            elif action == 'bill':
                err = self._check_pin(user, pin, lang)
                if err: return err
                amount = extract_amount(message)
                bill_type = extract_bill_type(message)
                if amount:
                    success, msg, txn = process_payment(
                        user, amount, Transaction.TYPE_BILL_PAYMENT,
                        description=f"Bill: {bill_type}")
                    wallet = Wallet.get_or_create_for_user(user)
                    if success:
                        return {
                            'answer': action_response('bill_success', lang,
                                                      type=bill_type, amount=amount,
                                                      balance=wallet.balance),
                            'intent': 'bill_payment', 'action': 'bill',
                            'lang': lang, 'source': 'action',
                        }
                    else:
                        return {
                            'answer': action_response('insufficient_balance', lang,
                                                      balance=wallet.balance),
                            'intent': 'bill_failed', 'lang': lang, 'source': 'action',
                        }
                else:
                    return {
                        'answer': action_response('bill_need_info', lang),
                        'intent': 'bill_info', 'lang': lang, 'source': 'action_guide',
                    }

            elif action == 'withdrawal':
                err = self._check_pin(user, pin, lang)
                if err: return err
                amount = extract_amount(message)
                if amount:
                    success, msg, txn = process_payment(
                        user, amount, Transaction.TYPE_WITHDRAWAL,
                        description="Cash withdrawal")
                    wallet = Wallet.get_or_create_for_user(user)
                    if success:
                        return {
                            'answer': action_response('withdrawal_success', lang,
                                                      amount=amount, balance=wallet.balance),
                            'intent': 'withdrawal', 'action': 'withdrawal',
                            'lang': lang, 'source': 'action',
                        }
                    else:
                        return {
                            'answer': action_response('insufficient_balance', lang,
                                                      balance=wallet.balance),
                            'intent': 'withdrawal_failed', 'lang': lang, 'source': 'action',
                        }

            elif action == 'gimtel':
                err = self._check_pin(user, pin, lang)
                if err: return err
                amount = extract_amount(message)
                app = extract_gimtel_app(message)
                if amount and app:
                    success, msg, txn = process_payment(
                        user, amount, Transaction.TYPE_GIMTEL,
                        description=f"GIMTEL to {app}")
                    wallet = Wallet.get_or_create_for_user(user)
                    if success:
                        return {
                            'answer': action_response('gimtel_success', lang,
                                                      app=app, amount=amount,
                                                      balance=wallet.balance),
                            'intent': 'gimtel', 'action': 'gimtel',
                            'lang': lang, 'source': 'action',
                        }
                    else:
                        return {
                            'answer': action_response('insufficient_balance', lang,
                                                      balance=wallet.balance),
                            'intent': 'gimtel_failed', 'lang': lang, 'source': 'action',
                        }

        # ════════════════════════════════════════════════════════════════════
        # LAYER 3 — FAQ keyword matching (offline fallback)
        # ════════════════════════════════════════════════════════════════════
        best_item, best_score = _match_faq(norm, lang)

        if best_item and best_score > CONFIDENCE_THRESHOLD:
            answer_key = f'answer_{lang}'
            answer = best_item.get(answer_key, best_item.get('answer_en', ''))
            return {
                'answer': answer,
                'intent': best_item.get('category', 'faq').lower(),
                'lang': lang, 'source': 'faq',
            }

        return {
            'answer': UNKNOWN_RESPONSE.get(lang, UNKNOWN_RESPONSE['en']),
            'intent': 'unknown', 'lang': lang, 'source': 'fallback',
        }


multilingual_engine = MultilingualIntentEngine()


# ── Social / courtesy matcher ─────────────────────────────────────────────────

_SOCIAL_PATTERNS = [
    # Thank you
    {
        'kw': {
            'ar': ['شكرا', 'شكراً', 'شكرا جزيلا', 'ممنون', 'مشكور', 'بارك الله', 'جزاك الله', 'يسلمو', 'مرسي'],
            'fr': ['merci', 'merci beaucoup', 'je vous remercie', 'grand merci', 'merci bien'],
            'en': ['thank you', 'thanks', 'thank u', 'thx', 'ty', 'many thanks', 'thanks a lot', 'thank you so much'],
        },
        'reply': {
            'ar': '😊 على الرحب والسعة! يسعدني مساعدتك دائماً. هل هناك شيء آخر يمكنني مساعدتك فيه؟',
            'fr': '😊 Avec plaisir ! Je suis toujours là pour vous aider. Autre chose ?',
            'en': '😊 You\'re very welcome! Happy to help anytime. Is there anything else I can do for you?',
        },
    },
    # Goodbye
    {
        'kw': {
            'ar': ['مع السلامة', 'وداعا', 'الى اللقاء', 'باي', 'وداع', 'تصبح على خير', 'يسعد مساك'],
            'fr': ['au revoir', 'bonne journée', 'bonne nuit', 'à bientôt', 'bye', 'ciao', 'à plus'],
            'en': ['bye', 'goodbye', 'good bye', 'see you', 'see ya', 'take care', 'good night', 'good day', 'farewell'],
        },
        'reply': {
            'ar': '👋 مع السلامة! أتمنى لك يوماً رائعاً ومليئاً بالخير. لا تتردد في العودة إذا احتجت مساعدة!',
            'fr': '👋 Au revoir ! Bonne journée, et n\'hésitez pas à revenir si vous avez besoin d\'aide !',
            'en': '👋 Goodbye! Have a wonderful day. Don\'t hesitate to come back whenever you need anything!',
        },
    },
    # Great / perfect / awesome
    {
        'kw': {
            'ar': ['رائع', 'ممتاز', 'عظيم', 'جميل', 'تمام', 'حلو', 'مذهل', 'ولا أروع', 'روعة', 'زين', 'بديع'],
            'fr': ['parfait', 'excellent', 'super', 'génial', 'fantastique', 'bravo', 'très bien', 'nickel', 'top'],
            'en': ['great', 'perfect', 'excellent', 'awesome', 'amazing', 'wonderful', 'fantastic', 'nice', 'cool', 'brilliant', 'superb'],
        },
        'reply': {
            'ar': '🌟 يسعدني أنك راضٍ! هل يمكنني مساعدتك في شيء آخر؟',
            'fr': '🌟 Ravi que cela vous convienne ! Puis-je vous aider avec autre chose ?',
            'en': '🌟 Glad to hear that! Can I help you with anything else?',
        },
    },
    # OK / alright / understood
    {
        'kw': {
            'ar': ['حسنا', 'حسناً', 'اوكي', 'موافق', 'فهمت', 'مفهوم', 'واضح', 'اوك', 'تمام تمام', 'ماشي'],
            'fr': ['ok', 'okay', 'd\'accord', 'compris', 'entendu', 'bien noté', 'ça marche', 'c\'est bon'],
            'en': ['ok', 'okay', 'alright', 'got it', 'understood', 'i see', 'noted', 'sure', 'makes sense'],
        },
        'reply': {
            'ar': '👍 ممتاز! هل تحتاج إلى مساعدة في أي شيء آخر؟',
            'fr': '👍 Bien ! Y a-t-il autre chose que je puisse faire pour vous ?',
            'en': '👍 Great! Is there anything else I can help you with?',
        },
    },
    # Sorry / apology
    {
        'kw': {
            'ar': ['آسف', 'اسف', 'معذرة', 'عفوا', 'أعتذر', 'اعتذر', 'اسمحلي', 'سامحني'],
            'fr': ['désolé', 'pardon', 'excusez-moi', 'je m\'excuse', 'toutes mes excuses', 'navré'],
            'en': ['sorry', 'i\'m sorry', 'my apologies', 'apologies', 'excuse me', 'pardon', 'my bad', 'forgive me'],
        },
        'reply': {
            'ar': '😊 لا داعي للاعتذار على الإطلاق! أنا هنا دائماً للمساعدة. كيف يمكنني خدمتك؟',
            'fr': '😊 Pas de souci du tout ! Je suis là pour vous aider. Comment puis-je vous être utile ?',
            'en': '😊 No worries at all! That\'s what I\'m here for. What can I do for you?',
        },
    },
    # Compliment the bot
    {
        'kw': {
            'ar': ['أنت رائع', 'أنت ذكي', 'مساعد ممتاز', 'خدمة رائعة', 'تطبيق ممتاز', 'أنت مميز', 'احبك'],
            'fr': ['tu es super', 'vous êtes super', 'excellent service', 'très utile', 'bien fait', 'je t\'aime', 'je vous aime'],
            'en': ['you are great', 'you\'re great', 'you\'re amazing', 'good bot', 'great service', 'very helpful', 'well done', 'i love you', 'love you'],
        },
        'reply': {
            'ar': '🤩 شكراً جزيلاً، هذا يجعلني سعيداً! يسعدني دائماً خدمتك. لا تتردد في السؤال عن أي شيء!',
            'fr': '🤩 Merci beaucoup, ça me touche vraiment ! C\'est un plaisir de vous aider. N\'hésitez pas !',
            'en': '🤩 Aww, thank you so much! That really means a lot. Feel free to ask me anything anytime!',
        },
    },
    # How are you
    {
        'kw': {
            'ar': ['كيف حالك', 'كيفك', 'عامل ايه', 'كيف الحال', 'ايش أخبارك', 'شو أخبارك', 'كيف أنت'],
            'fr': ['comment vas-tu', 'comment allez-vous', 'ça va', 'comment tu vas', 'tu vas bien'],
            'en': ['how are you', 'how r u', 'how are u', 'how\'s it going', 'how do you do', 'you doing well', 'how you doing'],
        },
        'reply': {
            'ar': '😄 أنا بخير جداً، شكراً لسؤالك! جاهز دائماً لمساعدتك. كيف يمكنني خدمتك اليوم؟',
            'fr': '😄 Je vais très bien, merci de demander ! Toujours prêt à vous aider. Comment puis-je vous servir aujourd\'hui ?',
            'en': '😄 I\'m doing great, thanks for asking! Always ready to help you out. How can I assist you today?',
        },
    },
    # What is your name / who are you
    {
        'kw': {
            'ar': ['ما اسمك', 'من أنت', 'مين انت', 'اسمك ايه', 'عرفني عليك', 'تعريف'],
            'fr': ['comment tu t\'appelles', 'qui es-tu', 'quel est ton nom', 'qui êtes-vous', 'ton nom'],
            'en': ['what is your name', 'what\'s your name', 'who are you', 'tell me about yourself', 'your name', 'introduce yourself'],
        },
        'reply': {
            'ar': '🤖 أنا FinAssist، مساعدك المالي الذكي! 💚\n\nأنا هنا لمساعدتك في كل ما يخص تطبيقك المالي:\n💰 الرصيد • 💸 التحويلات • 📱 شحن الهاتف\n🧾 الفواتير • 💵 السحب النقدي • 🔑 الرقم السري\n\nما الذي يمكنني مساعدتك فيه؟ 😊',
            'fr': '🤖 Je suis FinAssist, votre assistant financier intelligent ! 💚\n\nJe suis là pour vous aider avec tout ce qui concerne votre application:\n💰 Solde • 💸 Virements • 📱 Recharge\n🧾 Factures • 💵 Retrait • 🔑 Code PIN\n\nComment puis-je vous aider ? 😊',
            'en': '🤖 I\'m FinAssist, your smart financial assistant! 💚\n\nI\'m here to help you with everything in your app:\n💰 Balance • 💸 Transfers • 📱 Top-up\n🧾 Bills • 💵 Cash withdrawal • 🔑 PIN\n\nWhat can I do for you? 😊',
        },
    },
    # What can you do
    {
        'kw': {
            'ar': ['ماذا تستطيع', 'ايش تقدر تسوي', 'ايش تعرف', 'ما قدراتك', 'ايش خدماتك'],
            'fr': ['que peux-tu faire', 'qu\'est-ce que tu sais faire', 'tes capacités', 'tes fonctionnalités', 'quels services'],
            'en': ['what can you do', 'what do you do', 'what are your capabilities', 'what services', 'your features'],
        },
        'reply': {
            'ar': '✨ إليك ما يمكنني فعله:\n\n💰 عرض رصيدك الفعلي\n💸 تحويل الأموال\n📱 شحن الهاتف (موريتل / شنقيتل / ماتل)\n🧾 دفع الفواتير (كهرباء، ماء، إنترنت...)\n💵 سحب الأموال نقداً\n🏪 الدفع عند التجار (B-Pay)\n🔄 تحويل عبر GIMTEL\n🔑 مساعدتك بشأن الرقم السري\n\nما الذي تريد فعله؟ 😊',
            'fr': '✨ Voici ce que je peux faire:\n\n💰 Afficher votre solde réel\n💸 Effectuer des virements\n📱 Recharger votre téléphone\n🧾 Payer vos factures\n💵 Retrait d\'espèces\n🏪 Paiement marchand (B-Pay)\n🔄 Transferts GIMTEL\n🔑 Aide avec votre code PIN\n\nQue souhaitez-vous faire ? 😊',
            'en': '✨ Here\'s what I can do for you:\n\n💰 Show your real-time balance\n💸 Transfer money\n📱 Phone top-up\n🧾 Pay bills\n💵 Cash withdrawal\n🏪 Merchant payment (B-Pay)\n🔄 GIMTEL transfers\n🔑 PIN assistance\n\nWhat would you like to do? 😊',
        },
    },
    # Good morning / afternoon / evening
    {
        'kw': {
            'ar': ['صباح الخير', 'صباح النور', 'مساء الخير', 'مساء النور', 'صبح', 'مساء'],
            'fr': ['bonjour', 'bonsoir', 'bon matin', 'bonne soirée', 'salut'],
            'en': ['good morning', 'good afternoon', 'good evening', 'morning', 'evening', 'hi there', 'hey there', 'hello there'],
        },
        'reply': {
            'ar': '☀️ صباح الخير والسعادة! كيف يمكنني مساعدتك اليوم؟',
            'fr': '☀️ Bonjour ! Ravi de vous voir. Comment puis-je vous aider aujourd\'hui ?',
            'en': '☀️ Hello there! Great to see you. How can I help you today?',
        },
    },
    # I'm happy / feeling good
    {
        'kw': {
            'ar': ['أنا سعيد', 'أنا مبسوط', 'أنا بخير', 'زين', 'الحمدلله', 'بخير'],
            'fr': ['je suis heureux', 'je suis content', 'je vais bien', 'tout va bien', 'je suis ravi'],
            'en': ['i am happy', 'i\'m happy', 'feeling good', 'i\'m good', 'i\'m great', 'doing well', 'i\'m fine'],
        },
        'reply': {
            'ar': '😊 يسعدني سماع ذلك! السعادة معدية 😄 هل يمكنني مساعدتك في شيء اليوم؟',
            'fr': '😊 Ça fait plaisir d\'entendre ça ! La bonne humeur est contagieuse 😄 Puis-je vous aider avec quelque chose ?',
            'en': '😊 That\'s great to hear! Happiness is contagious 😄 Can I help you with anything today?',
        },
    },
    # I have a problem / issue
    {
        'kw': {
            'ar': ['عندي مشكلة', 'في مشكلة', 'ما قادر', 'ما يشتغل', 'خطأ', 'مشكلة في'],
            'fr': ['j\'ai un problème', 'ça ne marche pas', 'il y a un problème', 'erreur', 'problème avec'],
            'en': ['i have a problem', 'there\'s an issue', 'something is wrong', 'it\'s not working', 'error', 'problem with'],
        },
        'reply': {
            'ar': '😟 أنا آسف لسماع ذلك! سأساعدك في حل المشكلة.\n\nأخبرني بالتفصيل ما الذي يحدث وسأبذل قصارى جهدي لمساعدتك 💪',
            'fr': '😟 Je suis désolé d\'entendre ça ! Je vais vous aider à résoudre ce problème.\n\nDites-moi en détail ce qui se passe et je ferai de mon mieux pour vous aider 💪',
            'en': '😟 I\'m sorry to hear that! Let\'s get this sorted out together.\n\nTell me in detail what\'s happening and I\'ll do my best to help you 💪',
        },
    },
    # Please / need help
    {
        'kw': {
            'ar': ['ساعدني', 'محتاج مساعدة', 'ابي مساعدة', 'اريد مساعدة', 'ابغى مساعدة'],
            'fr': ['aidez-moi', 'j\'ai besoin d\'aide', 'pouvez-vous m\'aider', 'je ne sais pas quoi faire'],
            'en': ['help me', 'i need help', 'can you help', 'please help', 'i don\'t know what to do'],
        },
        'reply': {
            'ar': '🙋 بكل سرور! أنا هنا من أجلك 😊\n\nأخبرني بما تحتاجه وسأساعدك فوراً:\n💰 الرصيد • 💸 التحويل • 📱 الشحن\n🧾 الفواتير • 💵 السحب • 🔑 الرقم السري',
            'fr': '🙋 Bien sûr, je suis là pour vous ! 😊\n\nDites-moi ce dont vous avez besoin:\n💰 Solde • 💸 Virement • 📱 Recharge\n🧾 Factures • 💵 Retrait • 🔑 Code PIN',
            'en': '🙋 Of course, I\'m here for you! 😊\n\nTell me what you need:\n💰 Balance • 💸 Transfer • 📱 Top-up\n🧾 Bills • 💵 Withdrawal • 🔑 PIN',
        },
    },
]


def _match_social(norm: str, lang: str) -> str | None:
    """Return a social reply if the message matches a courtesy pattern, else None."""
    for pattern in _SOCIAL_PATTERNS:
        keywords = pattern['kw'].get(lang, pattern['kw']['en'])
        for kw in keywords:
            if kw in norm:
                return pattern['reply'].get(lang, pattern['reply']['en'])
    return None
