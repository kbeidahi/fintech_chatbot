"""
Multilingual Intent Engine — Inquiry Only
Supports: Arabic, French, English
Handles: FAQ answers + Gemini fallback for unknown questions
"""
import logging
import re
import json
import urllib.error
import urllib.request
from difflib import SequenceMatcher
from urllib.parse import quote
from typing import Optional

from django.conf import settings

from apps.faq.multilingual_faq import MULTILINGUAL_FAQ

logger = logging.getLogger(__name__)

# ── Language detection ────────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    """Detect Arabic, French, or English."""
    arabic_chars = len(re.findall(r'[؀-ۿ]', text))
    french_words = [
        'bonjour', 'salut', 'bonsoir', 'solde', 'virement', 'virer', 'recharge',
        'recharger', 'facture', 'retrait', 'retirer', 'achat', 'payer', 'paiement',
        'comment', 'mon', 'mes', 'je', 'vous', 'nous', 'est', 'les', 'des', 'une',
        'pour', 'faire', 'voir', 'quel', 'quelle', 'combien', 'aide', 'merci',
        'argent', 'compte', 'carte', 'code', 'frais', 'envoi', 'envoyer',
        'transférer', 'transfert', 'consulter', 'afficher', 'obtenir',
    ]
    text_lower = text.lower()

    if arabic_chars > 2:
        return 'ar'
    if any(re.search(rf'\b{re.escape(w)}\b', text_lower) for w in french_words):
        return 'fr'
    return 'en'


# ── Normalize text ────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s؀-ۿ]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# ── LLM system prompts ────────────────────────────────────────────────────────

LLM_SYSTEM_PROMPTS = {
    'ar': (
        'أنت FinAssist، مساعد استفسارات ذكي لتطبيق مالي. '
        'مهمتك الوحيدة هي الإجابة على أسئلة المستخدمين حول كيفية استخدام خدمات التطبيق: '
        'الرصيد، التحويل، شحن الهاتف، دفع الفواتير، السحب، GIMTEL، B-Pay، البطاقة، الرقم السري. '
        'أجب دائماً باللغة العربية عندما يكتب المستخدم بالعربية. '
        'كن مفصلاً وودوداً وواضحاً. لا تنفذ أي عملية مالية.'
    ),
    'fr': (
        'Vous êtes FinAssist, un assistant d\'information intelligent pour une application fintech. '
        'Votre seule mission est de répondre aux questions sur comment utiliser les services de l\'application: '
        'solde, virement, recharge, factures, retrait, GIMTEL, B-Pay, carte, PIN. '
        'Répondez toujours en français quand l\'utilisateur écrit en français. '
        'Soyez détaillé, amical et clair. N\'exécutez aucune transaction financière.'
    ),
    'en': (
        'You are FinAssist, a smart inquiry assistant for a fintech app. '
        'Your only job is to answer questions about how to use the app\'s services: '
        'balance, transfer, phone top-up, bill payment, cash withdrawal, GIMTEL, B-Pay, card, PIN. '
        'Always respond in the same language the user writes in. '
        'Be detailed, friendly and clear. Do not execute any financial transactions.'
    ),
}


# ── Gemini fallback ───────────────────────────────────────────────────────────

def gemini_fallback(user_message: str, lang: str) -> str:
    """Call Gemini for questions not covered by FAQ."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return ''
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash').strip()
    model_path = model if model.startswith('models/') else f'models/{model}'

    body = json.dumps({
        'system_instruction': {
            'parts': [{'text': LLM_SYSTEM_PROMPTS.get(lang, LLM_SYSTEM_PROMPTS['en'])}],
        },
        'contents': [{
            'role': 'user',
            'parts': [{'text': user_message}],
        }],
        'generationConfig': {
            'temperature': 0.3,
            'maxOutputTokens': 1024,
        },
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://generativelanguage.googleapis.com/v1beta/'
        f'{quote(model_path, safe="/")}:generateContent'
        f'?key={api_key}',
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.loads(response.read().decode('utf-8'))

    candidates = data.get('candidates') or []
    if not candidates:
        return ''
    parts = candidates[0].get('content', {}).get('parts') or []
    return ''.join(part.get('text', '') for part in parts).strip()


# ── Unknown response messages ─────────────────────────────────────────────────

UNKNOWN_RESPONSE = {
    'ar': (
        'عذراً، لم أفهم سؤالك تماماً 🤔\n\n'
        'يمكنني مساعدتك في:\n'
        '💰 معرفة الرصيد\n'
        '📱 شحن الهاتف\n'
        '💸 تحويل الأموال\n'
        '🔄 خدمة GIMTEL\n'
        '🧾 دفع الفواتير\n'
        '💵 سحب النقود\n'
        '🏪 الدفع عبر B-Pay\n'
        '💳 البطاقة والرقم السري\n\n'
        'حاول إعادة صياغة سؤالك!'
    ),
    'fr': (
        'Désolé, je n\'ai pas bien compris votre question 🤔\n\n'
        'Je peux vous aider avec:\n'
        '💰 Consulter le solde\n'
        '📱 Recharge téléphone\n'
        '💸 Virement d\'argent\n'
        '🔄 Service GIMTEL\n'
        '🧾 Paiement de factures\n'
        '💵 Retrait d\'espèces\n'
        '🏪 Paiement B-Pay\n'
        '💳 Carte et PIN\n\n'
        'Essayez de reformuler votre question!'
    ),
    'en': (
        'Sorry, I didn\'t quite understand your question 🤔\n\n'
        'I can help you with:\n'
        '💰 Check balance\n'
        '📱 Phone top-up\n'
        '💸 Money transfer\n'
        '🔄 GIMTEL service\n'
        '🧾 Bill payment\n'
        '💵 Cash withdrawal\n'
        '🏪 B-Pay merchant payment\n'
        '💳 Card and PIN\n\n'
        'Try rephrasing your question!'
    ),
}


# ── Main engine ───────────────────────────────────────────────────────────────

CONFIDENCE_THRESHOLD = 0.01  # any keyword match → FAQ; only score==0 goes to Gemini


class MultilingualIntentEngine:

    def _match_faq(self, norm_text: str, lang: str) -> tuple:
        """Returns (best_item, best_score)."""
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

    def resolve(self, message: str, user=None) -> dict:
        lang = detect_language(message)
        norm = normalize(message)

        # ── FAQ matching ──────────────────────────────────────────────────────
        best_item, best_score = self._match_faq(norm, lang)

        if best_item and best_score > CONFIDENCE_THRESHOLD:
            answer_key = f'answer_{lang}'
            answer = best_item.get(answer_key, best_item.get('answer_en', ''))
            return {
                'answer': answer,
                'intent': best_item.get('category', 'faq').lower(),
                'lang': lang,
                'source': 'faq',
            }

        # ── Gemini fallback for unknown questions ─────────────────────────────
        if settings.GEMINI_API_KEY:
            try:
                answer = gemini_fallback(message, lang)
                if answer:
                    return {
                        'answer': answer,
                        'intent': 'gemini_fallback',
                        'confidence': 0.5,
                        'lang': lang,
                        'source': 'gemini',
                    }
                logger.error('Gemini returned empty response')
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode('utf-8', errors='replace')
                logger.error('Gemini HTTP %s: %s', exc.code, detail)
            except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
                logger.exception('Gemini fallback failed: %s', exc)

        # ── Final fallback ────────────────────────────────────────────────────
        return {
            'answer': UNKNOWN_RESPONSE.get(lang, UNKNOWN_RESPONSE['en']),
            'intent': 'unknown',
            'lang': lang,
            'source': 'fallback',
        }


# Singleton
multilingual_engine = MultilingualIntentEngine()
