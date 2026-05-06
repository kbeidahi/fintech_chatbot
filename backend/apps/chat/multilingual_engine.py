"""
Multilingual Intent Engine
Supports: Arabic, French, English
Handles: FAQ answers + real financial actions
"""
import re
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from typing import Optional

from django.contrib.auth import get_user_model

from apps.faq.multilingual_faq import MULTILINGUAL_FAQ
from apps.wallet.models import (
    Wallet, transfer_funds, process_payment, Transaction
)

User = get_user_model()

# ── Language detection ────────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    """Detect Arabic, French, or English."""
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    french_words = ['bonjour', 'salut', 'solde', 'virement', 'virer', 'recharge',
                    'facture', 'retrait', 'achat', 'payer', 'comment', 'mon', 'mes',
                    'je', 'vous', 'nous', 'est', 'les', 'des', 'une', 'pour']
    text_lower = text.lower()

    if arabic_chars > 2:
        return 'ar'
    if any(w in text_lower for w in french_words):
        return 'fr'
    return 'en'


# ── Normalize text ────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# ── Amount & reference extraction ─────────────────────────────────────────────

def extract_amount(text: str) -> Optional[Decimal]:
    """Extract numeric amount from text."""
    match = re.search(r'\b(\d+(?:[.,]\d+)?)\b', text)
    if match:
        try:
            return Decimal(match.group(1).replace(',', '.'))
        except InvalidOperation:
            return None
    return None


def extract_username(text: str) -> Optional[str]:
    """Extract target username from transfer text."""
    patterns = [
        r'(?:to|إلى|à|pour|vers)\s+(\w+)',
        r'(?:transfer|حول|virer|envoyer)\s+\d+\s+(?:to|إلى|à)\s+(\w+)',
        r'(\w+)$',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group(1)
            if candidate.lower() not in ['to', 'à', 'pour', 'vers', 'إلى']:
                return candidate
    return None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    match = re.search(r'\b(\d{8,12})\b', text)
    return match.group(1) if match else None


def extract_bill_type(text: str) -> str:
    """Extract bill type from text."""
    text_lower = text.lower()
    if any(w in text_lower for w in ['كهرباء', 'électricité', 'electricity', 'electric']):
        return 'electricity'
    if any(w in text_lower for w in ['ماء', 'eau', 'water']):
        return 'water'
    if any(w in text_lower for w in ['انترنت', 'internet']):
        return 'internet'
    return 'general'


def extract_gimtel_app(text: str) -> Optional[str]:
    """Extract GIMTEL target app from text."""
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


# ── Response messages ─────────────────────────────────────────────────────────

RESPONSES = {
    'balance_result': {
        'ar': 'رصيدك الحالي هو: {balance} {currency} 💰',
        'fr': 'Votre solde actuel est: {balance} {currency} 💰',
        'en': 'Your current balance is: {balance} {currency} 💰',
    },
    'transfer_success': {
        'ar': '✅ تم التحويل بنجاح!\nالمبلغ: {amount} MRU\nإلى: {receiver}\nرصيدك الجديد: {balance} MRU',
        'fr': '✅ Virement effectué avec succès!\nMontant: {amount} MRU\nVers: {receiver}\nNouveau solde: {balance} MRU',
        'en': '✅ Transfer successful!\nAmount: {amount} MRU\nTo: {receiver}\nNew balance: {balance} MRU',
    },
    'transfer_failed': {
        'ar': '❌ فشل التحويل: {reason}',
        'fr': '❌ Virement échoué: {reason}',
        'en': '❌ Transfer failed: {reason}',
    },
    'transfer_need_info': {
        'ar': 'لتحويل الأموال، أرسل: "حول [المبلغ] إلى [اسم المستخدم]"\nمثال: حول 500 إلى ahmed',
        'fr': 'Pour faire un virement, tapez: "virer [montant] à [utilisateur]"\nExemple: virer 500 à ahmed',
        'en': 'To transfer money, type: "transfer [amount] to [username]"\nExample: transfer 500 to ahmed',
    },
    'topup_success': {
        'ar': '✅ تم شحن الهاتف بنجاح!\nالرقم: {phone}\nالمبلغ: {amount} MRU\nرصيدك الجديد: {balance} MRU',
        'fr': '✅ Recharge effectuée!\nNuméro: {phone}\nMontant: {amount} MRU\nNouveau solde: {balance} MRU',
        'en': '✅ Phone topped up successfully!\nNumber: {phone}\nAmount: {amount} MRU\nNew balance: {balance} MRU',
    },
    'topup_need_info': {
        'ar': 'لشحن الهاتف، أرسل: "شحن [رقم الهاتف] بمبلغ [المبلغ]"\nمثال: شحن 22334455 بمبلغ 100',
        'fr': 'Pour recharger, tapez: "recharge [numéro] montant [montant]"\nExemple: recharge 22334455 montant 100',
        'en': 'To top up, type: "topup [phone] amount [amount]"\nExample: topup 22334455 amount 100',
    },
    'payment_success': {
        'ar': '✅ تم الدفع بنجاح!\nالنوع: {type}\nالمبلغ: {amount} MRU\nرصيدك الجديد: {balance} MRU',
        'fr': '✅ Paiement effectué!\nType: {type}\nMontant: {amount} MRU\nNouveau solde: {balance} MRU',
        'en': '✅ Payment successful!\nType: {type}\nAmount: {amount} MRU\nNew balance: {balance} MRU',
    },
    'payment_need_info': {
        'ar': 'لدفع الفاتورة، أرسل: "دفع فاتورة [النوع] بمبلغ [المبلغ]"\nمثال: دفع فاتورة كهرباء 500',
        'fr': 'Pour payer une facture, tapez: "payer facture [type] montant [montant]"\nExemple: payer facture électricité 500',
        'en': 'To pay a bill, type: "pay bill [type] amount [amount]"\nExample: pay bill electricity 500',
    },
    'withdrawal_success': {
        'ar': '✅ تم السحب بنجاح!\nالمبلغ: {amount} MRU\nرصيدك الجديد: {balance} MRU\nيرجى استلام النقود من أقرب صراف آلي.',
        'fr': '✅ Retrait effectué!\nMontant: {amount} MRU\nNouveau solde: {balance} MRU\nVeuillez retirer l\'argent au distributeur le plus proche.',
        'en': '✅ Withdrawal successful!\nAmount: {amount} MRU\nNew balance: {balance} MRU\nPlease collect cash from the nearest ATM.',
    },
    'gimtel_success': {
        'ar': '✅ تم التحويل عبر GIMTEL بنجاح!\nإلى: {app}\nالمبلغ: {amount} MRU\nرصيدك الجديد: {balance} MRU',
        'fr': '✅ Virement GIMTEL effectué!\nVers: {app}\nMontant: {amount} MRU\nNouveau solde: {balance} MRU',
        'en': '✅ GIMTEL transfer successful!\nTo: {app}\nAmount: {amount} MRU\nNew balance: {balance} MRU',
    },
    'gimtel_need_info': {
        'ar': 'لتحويل GIMTEL، أرسل: "جيمتل [اسم التطبيق] [المبلغ]"\nمثال: جيمتل بنكيلي 500',
        'fr': 'Pour un virement GIMTEL, tapez: "gimtel [app] [montant]"\nExemple: gimtel bankily 500',
        'en': 'For GIMTEL transfer, type: "gimtel [app] [amount]"\nExample: gimtel bankily 500',
    },
    'user_not_found': {
        'ar': 'المستخدم "{username}" غير موجود. تحقق من اسم المستخدم وحاول مرة أخرى.',
        'fr': 'L\'utilisateur "{username}" n\'existe pas. Vérifiez le nom et réessayez.',
        'en': 'User "{username}" not found. Please check the username and try again.',
    },
    'insufficient_balance': {
        'ar': 'رصيدك غير كافٍ. رصيدك الحالي: {balance} MRU',
        'fr': 'Solde insuffisant. Votre solde actuel: {balance} MRU',
        'en': 'Insufficient balance. Your current balance: {balance} MRU',
    },
    'unknown': {
        'ar': 'عذراً، لم أفهم طلبك. يمكنني مساعدتك في: الرصيد، التحويل، شحن الهاتف، دفع الفواتير، السحب، GIMTEL.',
        'fr': 'Désolé, je n\'ai pas compris votre demande. Je peux vous aider avec: solde, virement, recharge, factures, retrait, GIMTEL.',
        'en': 'Sorry, I did not understand your request. I can help with: balance, transfer, phone topup, bills, withdrawal, GIMTEL.',
    },
}


def get_response(key: str, lang: str, **kwargs) -> str:
    template = RESPONSES.get(key, {}).get(lang, RESPONSES.get(key, {}).get('en', ''))
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


# ── Main engine ───────────────────────────────────────────────────────────────

CONFIDENCE_THRESHOLD = 0.25


class MultilingualIntentEngine:

    def _match_faq(self, norm_text: str, lang: str) -> tuple:
        """Returns (best_item, best_score)"""
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
                    score += 1.0
                elif kw:
                    words = norm_text.split()
                    best = max((similarity(w, kw) for w in words), default=0)
                    if best >= 0.75:
                        score += best * 0.6

            if keywords:
                score = min(score / len(keywords), 1.0)

            q_key = f'question_{lang}'
            if q_key in item:
                q_sim = similarity(norm_text, normalize(item[q_key]))
                score = max(score, q_sim * 0.8)

            if score > best_score:
                best_score = score
                best_item = item

        return best_item, best_score

    def resolve(self, message: str, user=None) -> dict:
        lang = detect_language(message)
        norm = normalize(message)

        # ── Check balance action ──────────────────────────────────────────────
        balance_keywords = {
            'ar': ['رصيد', 'رصيدي', 'كم عندي', 'اعرض رصيد'],
            'fr': ['solde', 'mon solde', 'voir solde', 'afficher solde'],
            'en': ['balance', 'my balance', 'show balance', 'check balance'],
        }
        if user and any(k in norm for k in balance_keywords.get(lang, [])):
            wallet = Wallet.get_or_create_for_user(user)
            return {
                'answer': get_response('balance_result', lang,
                                       balance=wallet.balance,
                                       currency=wallet.currency),
                'intent': 'check_balance',
                'action': 'check_balance',
                'lang': lang,
                'source': 'action',
            }

        # ── Transfer action ───────────────────────────────────────────────────
        transfer_keywords = {
            'ar': ['حول', 'تحويل', 'ارسل', 'أرسل'],
            'fr': ['virer', 'virement', 'transférer', 'envoyer'],
            'en': ['transfer', 'send money', 'send'],
        }
        if user and any(k in norm for k in transfer_keywords.get(lang, [])):
            amount = extract_amount(message)
            username = extract_username(message)

            if amount and username:
                try:
                    receiver = User.objects.get(username=username)
                    success, msg, txn = transfer_funds(user, receiver, amount)
                    if success:
                        wallet = Wallet.get_or_create_for_user(user)
                        return {
                            'answer': get_response('transfer_success', lang,
                                                   amount=amount,
                                                   receiver=username,
                                                   balance=wallet.balance),
                            'intent': 'transfer',
                            'action': 'transfer',
                            'lang': lang,
                            'source': 'action',
                        }
                    else:
                        wallet = Wallet.get_or_create_for_user(user)
                        return {
                            'answer': get_response('insufficient_balance', lang,
                                                   balance=wallet.balance),
                            'intent': 'transfer_failed',
                            'action': 'transfer',
                            'lang': lang,
                            'source': 'action',
                        }
                except User.DoesNotExist:
                    return {
                        'answer': get_response('user_not_found', lang, username=username),
                        'intent': 'transfer_failed',
                        'lang': lang,
                        'source': 'action',
                    }
            else:
                return {
                    'answer': get_response('transfer_need_info', lang),
                    'intent': 'transfer_info',
                    'lang': lang,
                    'source': 'faq',
                }

        # ── Phone top-up action ───────────────────────────────────────────────
        topup_keywords = {
            'ar': ['شحن', 'اشحن', 'رصيد هاتف', 'شحن موبايل'],
            'fr': ['recharge', 'recharger', 'crédit téléphonique'],
            'en': ['topup', 'top up', 'recharge', 'phone credit'],
        }
        if user and any(k in norm for k in topup_keywords.get(lang, [])):
            amount = extract_amount(message)
            phone = extract_phone(message)

            if amount and phone:
                success, msg, txn = process_payment(
                    user, amount,
                    Transaction.TYPE_PHONE_TOPUP,
                    description=f"Phone top-up: {phone}"
                )
                if success:
                    wallet = Wallet.get_or_create_for_user(user)
                    return {
                        'answer': get_response('topup_success', lang,
                                               phone=phone, amount=amount,
                                               balance=wallet.balance),
                        'intent': 'phone_topup',
                        'action': 'phone_topup',
                        'lang': lang,
                        'source': 'action',
                    }
                else:
                    wallet = Wallet.get_or_create_for_user(user)
                    return {
                        'answer': get_response('insufficient_balance', lang,
                                               balance=wallet.balance),
                        'intent': 'topup_failed',
                        'lang': lang,
                        'source': 'action',
                    }
            else:
                return {
                    'answer': get_response('topup_need_info', lang),
                    'intent': 'phone_topup_info',
                    'lang': lang,
                    'source': 'faq',
                }

        # ── Bill payment action ───────────────────────────────────────────────
        bill_keywords = {
            'ar': ['فاتورة', 'دفع فاتورة', 'سداد فاتورة'],
            'fr': ['facture', 'payer facture', 'régler facture'],
            'en': ['bill', 'pay bill', 'electricity bill', 'water bill'],
        }
        if user and any(k in norm for k in bill_keywords.get(lang, [])):
            amount = extract_amount(message)
            bill_type = extract_bill_type(message)

            if amount:
                success, msg, txn = process_payment(
                    user, amount,
                    Transaction.TYPE_BILL_PAYMENT,
                    description=f"Bill payment: {bill_type}"
                )
                if success:
                    wallet = Wallet.get_or_create_for_user(user)
                    return {
                        'answer': get_response('payment_success', lang,
                                               type=bill_type, amount=amount,
                                               balance=wallet.balance),
                        'intent': 'bill_payment',
                        'action': 'bill_payment',
                        'lang': lang,
                        'source': 'action',
                    }
                else:
                    wallet = Wallet.get_or_create_for_user(user)
                    return {
                        'answer': get_response('insufficient_balance', lang,
                                               balance=wallet.balance),
                        'intent': 'payment_failed',
                        'lang': lang,
                        'source': 'action',
                    }
            else:
                return {
                    'answer': get_response('payment_need_info', lang),
                    'intent': 'bill_payment_info',
                    'lang': lang,
                    'source': 'faq',
                }

        # ── Withdrawal action ─────────────────────────────────────────────────
        withdrawal_keywords = {
            'ar': ['سحب', 'أسحب', 'سحب نقود'],
            'fr': ['retrait', 'retirer', 'retirer argent'],
            'en': ['withdraw', 'withdrawal', 'cash out'],
        }
        if user and any(k in norm for k in withdrawal_keywords.get(lang, [])):
            amount = extract_amount(message)
            if amount:
                success, msg, txn = process_payment(
                    user, amount,
                    Transaction.TYPE_WITHDRAWAL,
                    description="Cash withdrawal"
                )
                if success:
                    wallet = Wallet.get_or_create_for_user(user)
                    return {
                        'answer': get_response('withdrawal_success', lang,
                                               amount=amount,
                                               balance=wallet.balance),
                        'intent': 'withdrawal',
                        'action': 'withdrawal',
                        'lang': lang,
                        'source': 'action',
                    }
                else:
                    wallet = Wallet.get_or_create_for_user(user)
                    return {
                        'answer': get_response('insufficient_balance', lang,
                                               balance=wallet.balance),
                        'intent': 'withdrawal_failed',
                        'lang': lang,
                        'source': 'action',
                    }

        # ── GIMTEL transfer action ────────────────────────────────────────────
        gimtel_keywords = {
            'ar': ['جيمتل', 'بنكيلي', 'كليك', 'سيداد', 'باميس', 'مصرفي'],
            'fr': ['gimtel', 'bankily', 'click', 'sedad', 'bamis', 'masrivi'],
            'en': ['gimtel', 'bankily', 'click', 'sedad', 'bamis', 'masrivi'],
        }
        if user and any(k in norm for k in gimtel_keywords.get(lang, [])):
            amount = extract_amount(message)
            app = extract_gimtel_app(message)

            if amount and app:
                success, msg, txn = process_payment(
                    user, amount,
                    Transaction.TYPE_GIMTEL,
                    description=f"GIMTEL transfer to {app}"
                )
                if success:
                    wallet = Wallet.get_or_create_for_user(user)
                    return {
                        'answer': get_response('gimtel_success', lang,
                                               app=app, amount=amount,
                                               balance=wallet.balance),
                        'intent': 'gimtel_transfer',
                        'action': 'gimtel',
                        'lang': lang,
                        'source': 'action',
                    }
                else:
                    wallet = Wallet.get_or_create_for_user(user)
                    return {
                        'answer': get_response('insufficient_balance', lang,
                                               balance=wallet.balance),
                        'intent': 'gimtel_failed',
                        'lang': lang,
                        'source': 'action',
                    }
            else:
                return {
                    'answer': get_response('gimtel_need_info', lang),
                    'intent': 'gimtel_info',
                    'lang': lang,
                    'source': 'faq',
                }

        # ── FAQ matching ──────────────────────────────────────────────────────
        best_item, best_score = self._match_faq(norm, lang)

        if best_item and best_score >= CONFIDENCE_THRESHOLD:
            answer_key = f'answer_{lang}'
            answer = best_item.get(answer_key, best_item.get('answer_en', ''))
            return {
                'answer': answer,
                'intent': best_item.get('category', 'faq').lower(),
                'lang': lang,
                'source': 'faq',
            }

        # ── Default fallback ──────────────────────────────────────────────────
        return {
            'answer': get_response('unknown', lang),
            'intent': 'unknown',
            'lang': lang,
            'source': 'fallback',
        }


# Singleton
multilingual_engine = MultilingualIntentEngine()
