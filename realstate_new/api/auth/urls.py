from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import ChangePasswordView
from .views import GoogleVerificationView
from .views import LoginView
from .views import PasswordResetAfterVerificationView
from .views import PasswordResetOTPVerifyView
from .views import RegistrationView
from .views import SendPasswordResetOTPView
from .views import UserResetPasswordView
from .views import confirm_user

app_name = "auth"

urlpatterns = [
    path(
        "registration",
        RegistrationView.as_view(),
    ),
    path("confirm/<uid>/<token>", confirm_user, name="confirm-user"),
    path(
        "sendresetpasswordotp",
        SendPasswordResetOTPView.as_view(),
        name="send-reset-password",
    ),
    path(
        "resetpassword/<uid>/<token>",
        UserResetPasswordView.as_view(),
        name="reset-password",
    ),
    path(
        "passwordresetverifyotp",
        PasswordResetOTPVerifyView.as_view(),
        name="password-reset-verify-otp",
    ),
    path(
        "resetpassword",
        PasswordResetAfterVerificationView.as_view(),
    ),
    path("login", LoginView.as_view()),
    path("changepassword", ChangePasswordView.as_view(), name="change-password"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("google", GoogleVerificationView.as_view(), name="google-auth"),
]
