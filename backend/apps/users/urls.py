from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import LoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="token-obtain-pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]

