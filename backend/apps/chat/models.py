"""Chat models: Session and Message."""
import uuid
from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """A conversation thread between a user and the bot."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)  

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Session {self.id} — {self.user}"


class Message(models.Model):
    ROLE_CHOICES = [("user", "User"), ("bot", "Bot")]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    intent = models.CharField(max_length=100, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    faq_ref = models.ForeignKey(
        "faq.FAQItem", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}"
