"""
Intent engine — classifies incoming user messages and returns answers.

Pipeline:
  1. Normalize & tokenize message
  2. Match against FAQ keywords (exact + fuzzy)
  3. If confidence >= threshold → return FAQ answer
  4. Else → LLM fallback (optional) or polite "I don't know" reply
"""
import re
import logging
from difflib import SequenceMatcher
from typing import Optional

from django.conf import settings
from django.core.cache import cache

from apps.faq.models import FAQItem


logger = logging.getLogger(__name__)


def _normalize(text: str) -> str:
    """Lower-case, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _keyword_score(message_norm: str, keywords: list[str]) -> float:
    """
    Returns a 0–1 score based on keyword presence.
    Exact substring match scores 1.0 per keyword;
    fuzzy match adds a partial score.
    """
    if not keywords:
        return 0.0

    total = 0.0
    for kw in keywords:
        kw_norm = _normalize(kw)
        if kw_norm in message_norm:
            total += 1.0
        else:
            words = message_norm.split()
            best = max((_similarity(w, kw_norm) for w in words), default=0)
            if best >= 0.80:
                total += best * 0.5

    return min(total / max(len(keywords), 1), 1.0)




CONFIDENCE_THRESHOLD = 0.35
GREETING_PATTERNS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening", "hola"}
THANKS_PATTERNS = {"thanks", "thank you", "thx", "ty", "great", "perfect", "got it"}


class IntentEngine:
    """
    Stateless engine — create once, call .resolve() per message.
    Caches FAQ items in Redis for 5 minutes.
    """

    CACHE_KEY = "faq:items:all"
    CACHE_TTL = 300  # 5 minutes

    def _get_faq_items(self) -> list[FAQItem]:
        cached = cache.get(self.CACHE_KEY)
        if cached is not None:
            return cached
        items = list(FAQItem.objects.filter(is_active=True).select_related("category"))
        cache.set(self.CACHE_KEY, items, self.CACHE_TTL)
        return items

    def resolve(self, message: str, session_context: Optional[dict] = None) -> dict:
        """
        Returns:
            {
                "answer": str,
                "intent": str,      # slug label
                "confidence": float,
                "faq_id": int | None,
                "source": "faq" | "greeting" | "thanks" | "fallback",
            }
        """
        norm = _normalize(message)

        
        if any(g in norm for g in GREETING_PATTERNS):
            return {
                "answer": (
                    "Hello! I'm your FinTech assistant. I can help you with account management, "
                    "transfers, cards, fees, security, and loans. What can I help you with today?"
                ),
                "intent": "greeting",
                "confidence": 1.0,
                "faq_id": None,
                "source": "greeting",
            }

        # ── Thanks ────────────────────────────────────────────────────────────
        if any(t in norm for t in THANKS_PATTERNS):
            return {
                "answer": "You're welcome! Is there anything else I can help you with?",
                "intent": "thanks",
                "confidence": 1.0,
                "faq_id": None,
                "source": "thanks",
            }

        
        items = self._get_faq_items()
        best_score = 0.0
        best_item: Optional[FAQItem] = None

        for item in items:
            
            kw_score = _keyword_score(norm, item.keyword_list())
            
            q_sim = _similarity(norm, _normalize(item.question))
            score = max(kw_score, q_sim * 0.8)

            if score > best_score:
                best_score = score
                best_item = item

        if best_item and best_score >= CONFIDENCE_THRESHOLD:
            return {
                "answer": best_item.answer,
                "intent": best_item.category.name.lower().replace(" ", "_"),
                "confidence": round(best_score, 3),
                "faq_id": best_item.id,
                "source": "faq",
            }

        
        if settings.GEMINI_API_KEY:
            try:
                answer = _gemini_fallback(message)
                if answer:
                    return {
                        "answer": answer,
                        "intent": "gemini_fallback",
                        "confidence": 0.7,
                        "faq_id": None,
                        "source": "gemini",
                    }
            except Exception:
                pass
        return {
           "answer": (
                "عذراً، لم أفهم سؤالك. يمكنني المساعدة في: "
                "الرصيد، التحويل، الشحن، الفواتير، السحب، جيمتل، B-Pay.\n\n"
                "Sorry, I didn't understand. I can help with: "
                "balance, transfer, recharge, bills, withdrawal, GIMTEL, B-Pay."
                ),
            "intent": "unknown",
            "confidence": 0.0,
            "faq_id": None,
            "source": "fallback",
        }        



import urllib.request
import json

def _gemini_fallback(user_message: str) -> str:
    """Free Gemini AI fallback — no pip install needed."""

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    system_prompt = """You are a helpful customer support assistant for a fintech company name Finassist.
You answer questions about:
- Account balance and statements
- Money transfers
- Phone recharge (Mauritel, Chinguitel, Mattel)
- Bill payments (electricity, water, internet)
- Cash withdrawal via agency
- GIMTEL transfers to other apps (Bankily, Click, Sedad, Masrivi)
- B-Pay merchant payments
- Debit cards and cheque books
- PIN management
yo can also answer general answer and talk with clients

Answer in the same language the user wrote in (Arabic, French, or English).
Be concise, friendly and helpful.
"""

    body = json.dumps({
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [{
            "parts": [{"text": user_message}]
        }]
    }).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return None






intent_engine = IntentEngine()
