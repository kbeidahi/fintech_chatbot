"""
Intent engine — classifies incoming user messages and returns answers.

Pipeline:
  1. Normalize & tokenize message
  2. Match against FAQ keywords (exact + fuzzy)
  3. If confidence >= threshold → return FAQ answer
  4. Else → LLM fallback (optional) or polite "I don't know" reply
"""
import re
from difflib import SequenceMatcher
from typing import Optional

from django.conf import settings
from django.core.cache import cache

from apps.faq.models import FAQItem




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

        
        if settings.OPENAI_API_KEY:
            try:
                answer = _llm_fallback(message)
                return {
                    "answer": answer,
                    "intent": "llm_fallback",
                    "confidence": 0.5,
                    "faq_id": None,
                    "source": "fallback",
                }
            except Exception:
                pass  

        
        return {
            "answer": (
                "I'm sorry, I don't have a specific answer for that. "
                "You can reach our support team via live chat, email at support@fintechapp.com, "
                "or call 1-800-000-0000. Is there anything else I can help you with?"
            ),
            "intent": "unknown",
            "confidence": 0.0,
            "faq_id": None,
            "source": "fallback",
        }




def _llm_fallback(user_message: str) -> str:
    """Call OpenAI with a fintech-scoped system prompt."""
    import openai  

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful customer support assistant for a fintech company. "
                    "Answer only questions related to personal finance, banking, payments, cards, loans, "
                    "and account management. Be concise, friendly, and accurate. "
                    "If a question is outside your scope, politely redirect to human support."
                ),
            },
            {"role": "user", "content": user_message},
        ],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()



intent_engine = IntentEngine()
