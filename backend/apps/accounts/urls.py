# apps/accounts/urls.py
from django.urls import path
from .views import RegisterView, ProfileView, FindAccountView, ResetPasswordView, PinStatusView, SetPinView, VerifyPinView, sso_token_proxy, sso_userinfo_proxy

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("find-account/", FindAccountView.as_view(), name="find-account"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("pin/status/", PinStatusView.as_view(), name="pin-status"),
    path("pin/set/", SetPinView.as_view(), name="pin-set"),
    path("pin/verify/", VerifyPinView.as_view(), name="pin-verify"),
    path("sso/token/", sso_token_proxy, name="sso-token"),
    path("sso/userinfo/", sso_userinfo_proxy, name="sso-userinfo"),
]
