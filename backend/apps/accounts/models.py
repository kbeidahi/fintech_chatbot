"""Custom user model for fintech app."""
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True, default=None)
    preferred_language = models.CharField(max_length=10, default="en")
    created_at = models.DateTimeField(auto_now_add=True)
    pin_hash = models.CharField(max_length=128, blank=True, default="")

    class Meta:
        db_table = "accounts_user"

    def __str__(self):
        return self.email or self.username

    @property
    def has_pin(self) -> bool:
        return bool(self.pin_hash)

    def set_pin(self, raw_pin: str) -> None:
        """Hash and store a 4-digit PIN."""
        self.pin_hash = make_password(raw_pin)
        self.save(update_fields=["pin_hash"])

    def check_pin(self, raw_pin: str) -> bool:
        """Return True if raw_pin matches the stored hash."""
        if not self.pin_hash:
            return False
        return check_password(raw_pin, self.pin_hash)


class SsoPin(models.Model):
    """Stores whether an SSO user (identified by sub) has set a PIN."""
    sub = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "accounts_sso_pin"
