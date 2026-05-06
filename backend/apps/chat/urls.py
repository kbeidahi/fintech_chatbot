"""Chat URL patterns."""
from django.urls import path
from . import views

urlpatterns = [
    path("message/", views.SendMessageView.as_view(), name="chat-message"),
    path("sessions/", views.SessionListView.as_view(), name="chat-sessions"),
    path("sessions/<uuid:pk>/", views.SessionDetailView.as_view(), name="chat-session-detail"),
    path("sessions/<uuid:pk>/end/", views.EndSessionView.as_view(), name="chat-session-end"),
]
