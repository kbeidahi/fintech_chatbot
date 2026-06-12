"""Account registration, login, and profile views."""
import urllib.request, urllib.parse, json as _json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import generics, permissions, serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes as pc
from .models import SsoPin
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


# ── Serializers ──────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    phone    = serializers.CharField(required=True, min_length=8, max_length=20)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "phone", "preferred_language")

    def validate_username(self, value):
        return value.strip()

    def validate_email(self, value):
        return User.objects.normalize_email(value.strip())

    def validate_phone(self, value):
        value = value.strip()
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone", "preferred_language", "created_at")
        read_only_fields = ("id", "created_at")


def _token_payload_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }


class LoginSerializer(TokenObtainPairSerializer):
    """JWT login that accepts either username or email plus password."""

    def validate(self, attrs):
        login = attrs.get(self.username_field, "").strip()
        if "@" in login:
            user = User.objects.filter(email__iexact=login).order_by("id").first()
            if user is None:
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                )
            attrs[self.username_field] = user.username
        else:
            attrs[self.username_field] = login

        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
        }
        return data


# ── Views ────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        update_last_login(None, user)
        data = serializer.data
        data.update(_token_payload_for_user(user))
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/"""
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)


class PinStatusView(generics.GenericAPIView):
    """GET /api/auth/pin/status/ — check if user has set a PIN."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response({"has_pin": request.user.has_pin})


class SetPinView(generics.GenericAPIView):
    """POST /api/auth/pin/set/ — set or change the 4-digit PIN."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        pin = str(request.data.get("pin", "")).strip()
        if not pin.isdigit() or len(pin) != 4:
            return Response(
                {"error": "PIN must be exactly 4 digits."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.set_pin(pin)
        return Response({"message": "PIN set successfully."})


class VerifyPinView(generics.GenericAPIView):
    """POST /api/auth/pin/verify/ — verify PIN without executing any action."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        pin = str(request.data.get("pin", "")).strip()
        if request.user.check_pin(pin):
            return Response({"valid": True})
        return Response({"valid": False, "error": "Incorrect PIN."},
                        status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/profile/"""
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class FindAccountView(generics.GenericAPIView):
    """POST /api/auth/find-account/
    Body: { email }
    Returns the username if an account with that email exists.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "").strip()
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(
            email__iexact=User.objects.normalize_email(email)
        ).first()

        if user is None:
            return Response({"error": "No account found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"username": user.username})


class ResetPasswordView(generics.GenericAPIView):
    """POST /api/auth/reset-password/
    Body: { username, email, new_password }
    Validates that username + email match, then sets new password.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "").strip()
        email = request.data.get("email", "").strip()
        new_password = request.data.get("new_password", "")

        if not username or not email or not new_password:
            return Response(
                {"error": "Username, email and new password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 8:
            return Response(
                {"error": "New password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(
            username__iexact=username,
            email__iexact=User.objects.normalize_email(email),
        ).first()

        if user is None:
            return Response(
                {"error": "No account found with this username and email combination."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response({"message": "Password reset successfully. You can now log in."})


@api_view(["POST"])
@pc([permissions.AllowAny])
def sso_exchange(request):
    """Create or retrieve a Django User for an SSO identity, return JWT tokens."""
    try:
        sub   = request.data.get("sub", "").strip()
        email = request.data.get("email", "").strip()
        name  = request.data.get("name", "").strip()
        if not sub:
            return Response({"error": "sub required"}, status=400)

        username = f"sso_{sub[:120]}"
        # phone is NOT NULL + UNIQUE in DB; use a unique placeholder for SSO users
        sso_phone = f"sso_{sub[:50]}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email or "",
                "first_name": (name[:30] if name else ""),
                "phone": sso_phone,
            },
        )
        if not created and email and user.email != email:
            user.email = email
            user.save(update_fields=["email"])

        tokens = _token_payload_for_user(user)
        tokens['is_new_user'] = created
        return Response(tokens)
    except Exception as exc:
        import traceback
        return Response({"error": str(exc), "trace": traceback.format_exc()}, status=500)


@api_view(["GET", "POST"])
@pc([permissions.AllowAny])
def sso_pin_view(request):
    """GET ?sub=xxx → {has_pin: bool}   POST {sub} → saves pin flag."""
    if request.method == "GET":
        sub = request.query_params.get("sub", "").strip()
        return Response({"has_pin": SsoPin.objects.filter(sub=sub).exists()})
    sub = request.data.get("sub", "").strip()
    if not sub:
        return Response({"error": "sub required"}, status=400)
    SsoPin.objects.get_or_create(sub=sub)
    return Response({"ok": True})


@api_view(["POST"])
@pc([permissions.AllowAny])
def sso_token_proxy(request):
    """Server-side proxy for NovaGard /o/token/ to avoid CORS from the browser."""
    body = urllib.parse.urlencode({
        "grant_type":    request.data.get("grant_type", "authorization_code"),
        "code":          request.data.get("code", ""),
        "redirect_uri":  request.data.get("redirect_uri", ""),
        "client_id":     request.data.get("client_id", ""),
        "code_verifier": request.data.get("code_verifier", ""),
    }).encode()
    req = urllib.request.Request(
        "https://sso-backend-6b1e.onrender.com/o/token/",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _json.loads(resp.read())
            return Response(data)
    except urllib.error.HTTPError as e:
        return Response(_json.loads(e.read()), status=e.code)
    except Exception as exc:
        return Response({"error": str(exc)}, status=502)


@api_view(["GET"])
@pc([permissions.AllowAny])
def sso_userinfo_proxy(request):
    """Server-side proxy for NovaGard /o/userinfo/ to avoid CORS from the browser."""
    auth = request.headers.get("Authorization", "")
    req = urllib.request.Request(
        "https://sso-backend-6b1e.onrender.com/o/userinfo/",
        headers={"Authorization": auth},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return Response(_json.loads(resp.read()))
    except urllib.error.HTTPError as e:
        return Response(_json.loads(e.read()), status=e.code)
    except Exception as exc:
        return Response({"error": str(exc)}, status=502)

