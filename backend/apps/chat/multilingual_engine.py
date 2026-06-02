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
        'ar': 'لتحويل الأموال أرسل:\n**حول [المبلغ] إلى [اسم المستخدم]**\nمثال: حول 500 إلى ahmed',
        'fr': 'Pour virer, tapez:\n**virer [montant] à [utilisateur]**\nEx: virer 500 à ahmed',
        'en': 'To transfer, type:\n**transfer [amount] to [username]**\nEx: transfer 500 to ahmed',
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
        'ar': '❌ المستخدم **{username}** غير موجود.\nتحقق من اسم المستخدم وحاول مرة أخرى.',
        'fr': '❌ L\'utilisateur **{username}** introuvable.\nVérifiez le nom et réessayez.',
        'en': '❌ User **{username}** not found.\nCheck the username and try again.',
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

LLM_SYSTEM_PROMPTS = {
    'ar': (
        'أنت FinAssist، مساعد مالي ذكي وودود لتطبيق مالي رقمي. '
        'شخصيتك: دافئ، متحمس، مفيد جداً، وتستخدم إيموجي بشكل طبيعي. '
        'تتحدث مع المستخدم كصديق ذكي يفهم ماذا يريد المستخدم حتى لو لم يعبّر بشكل دقيق. '
        'حلّل نية المستخدم من كلامه وأجب بناءً على ما يريده فعلاً، ليس فقط الكلمات الحرفية. '
        '\n' + _APP_KNOWLEDGE +
        '\nأجب دائماً بالعربية الفصيحة أو العامية حسب ما يكتبه المستخدم. '
        'كن قصيراً وطبيعياً في المحادثة العادية، ومفصلاً وخطوة بخطوة في الأسئلة التقنية.'
    ),
    'fr': (
        'Vous êtes FinAssist, un assistant financier intelligent et chaleureux pour une application fintech. '
        'Personnalité: chaleureux, enthousiaste, très serviable, avec des emojis naturels. '
        'Vous parlez à l\'utilisateur comme un ami intelligent qui comprend ce qu\'il veut même s\'il ne s\'exprime pas précisément. '
        'Analysez l\'intention de l\'utilisateur et répondez en fonction de ce qu\'il veut vraiment. '
        '\n' + _APP_KNOWLEDGE +
        '\nRépondez toujours en français. Soyez bref et naturel en conversation, détaillé et étape par étape pour les questions techniques.'
    ),
    'en': (
        'You are FinAssist, a smart and friendly financial assistant for a digital fintech app. '
        'Personality: warm, enthusiastic, very helpful, and you use emojis naturally. '
        'You talk to the user like a smart knowledgeable friend who understands what they want even if they don\'t phrase it perfectly. '
        'Analyze the user\'s intent from their message and respond based on what they actually want, not just the literal words. '
        '\n' + _APP_KNOWLEDGE +
        '\nAlways reply in English. Be brief and natural in casual conversation, detailed and step-by-step for technical questions. '
        'If the user seems frustrated or confused, be extra supportive and ask clarifying questions.'
    ),
}


# ── Gemini fallback ───────────────────────────────────────────────────────────

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
        # LAYER 1 — ACTION (requires user + explicit command with amount)
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
                username = extract_username(message)
                if amount and username:
                    try:
                        receiver = User.objects.get(username=username)
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
        # LAYER 1.5 — SOCIAL / COURTESY (thank you, bye, compliments…)
        # ════════════════════════════════════════════════════════════════════
        social = _match_social(norm, lang)
        if social:
            return {'answer': social, 'intent': 'social', 'lang': lang, 'source': 'faq'}

        # ════════════════════════════════════════════════════════════════════
        # LAYER 2 — GEMINI (primary AI — understands intent from any phrasing)
        # ════════════════════════════════════════════════════════════════════
        if settings.GEMINI_API_KEY:
            try:
                answer = gemini_fallback(message, lang)
                if answer:
                    return {
                        'answer': answer,
                        'intent': 'gemini', 'confidence': 0.9,
                        'lang': lang, 'source': 'gemini',
                    }
                logger.error('Gemini returned empty response')
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode('utf-8', errors='replace')
                logger.error('Gemini HTTP %s: %s', exc.code, detail)
            except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
                logger.exception('Gemini failed: %s', exc)

        # ════════════════════════════════════════════════════════════════════
        # LAYER 3 — FAQ keyword matching (fast offline fallback)
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
