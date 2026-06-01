# apps/accounts/urls.py
from django.urls import path
from .views import RegisterView, ProfileView, FindAccountView, ResetPasswordView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("find-account/", FindAccountView.as_view(), name="find-account"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
