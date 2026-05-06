"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/faq/', include('apps.faq.urls')),
    path('api/wallet/', include('apps.wallet.urls')),
]
