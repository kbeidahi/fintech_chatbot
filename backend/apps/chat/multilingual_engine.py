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

LLM_SYSTEM_PROMPTS = {
    'ar': (
        'أنت FinAssist، مساعد استفسارات ذكي لتطبيق مالي. '
        'أجب على الأسئلة العامة حول استخدام التطبيق وخدماته: الرصيد، التحويل، شحن الهاتف، '
        'الفواتير، السحب، GIMTEL، B-Pay، البطاقة، الرقم السري. '
        'أجب دائماً بالعربية. كن مفصلاً وودوداً.'
    ),
    'fr': (
        'Vous êtes FinAssist, un assistant d\'information pour une application fintech. '
        'Répondez aux questions sur les services: solde, virement, recharge, factures, '
        'retrait, GIMTEL, B-Pay, carte, PIN. Répondez en français. Soyez détaillé et amical.'
    ),
    'en': (
        'You are FinAssist, a smart inquiry assistant for a fintech app. '
        'Answer questions about app services: balance, transfer, top-up, bills, '
        'withdrawal, GIMTEL, B-Pay, card, PIN. Be detailed, friendly and clear.'
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


def detect_action(norm: str, lang: str) -> Optional[str]:
    """
    Returns the action type only if the message looks like a COMMAND
    (contains action keyword + typically an amount or target).
    Simple inquiry questions like 'how do I transfer?' won't match.
    """
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
        # LAYER 2 — INQUIRY (FAQ + Gemini)
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

        # Gemini for truly unknown questions
        if settings.GEMINI_API_KEY:
            try:
                answer = gemini_fallback(message, lang)
                if answer:
                    return {
                        'answer': answer,
                        'intent': 'gemini_fallback', 'confidence': 0.5,
                        'lang': lang, 'source': 'gemini',
                    }
                logger.error('Gemini returned empty response')
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode('utf-8', errors='replace')
                logger.error('Gemini HTTP %s: %s', exc.code, detail)
            except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
                logger.exception('Gemini fallback failed: %s', exc)

        return {
            'answer': UNKNOWN_RESPONSE.get(lang, UNKNOWN_RESPONSE['en']),
            'intent': 'unknown', 'lang': lang, 'source': 'fallback',
        }


multilingual_engine = MultilingualIntentEngine()
