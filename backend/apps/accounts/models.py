"""Custom user model for fintech app."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    preferred_language = models.CharField(max_length=10, default="en")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_user"

    def __str__(self):
        return self.email or self.username
