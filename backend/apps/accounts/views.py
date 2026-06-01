"""Account registration, login, and profile views."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import generics, permissions, serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


# ── Serializers ──────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "phone", "preferred_language")

    def validate_username(self, value):
        return value.strip()

    def validate_email(self, value):
        return User.objects.normalize_email(value.strip())

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

