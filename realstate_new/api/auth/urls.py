from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import ChangePasswordView
from .views import GoogleVerificationView
from .views import LoginView
from .views import RegistrationView
from .views import SendPasswordResetView
from .views import UserResetPasswordView
from .views import confirm_user

app_name = "auth"

urlpatterns = [
    path(
        "registration",
        RegistrationView.as_view(),
    ),
    path("confirm/<uid>/<token>", confirm_user, name="confirm-user"),
    path("resetpassword", SendPasswordResetView.as_view(), name="send-reset-password"),
    path(
        "resetpassword/<uid>/<token>",
        UserResetPasswordView.as_view(),
        name="reset-password",
    ),
    path("login", LoginView.as_view()),
    path("changepassword", ChangePasswordView.as_view(), name="change-password"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("google", GoogleVerificationView.as_view(), name="google-auth"),
]
