import json
import logging
import random
import secrets

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_bytes
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import serializers
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from realstate_new.users.models import FCMDevice
from realstate_new.users.models import User as UserType
from realstate_new.utils import send_email
from realstate_new.utils.utils import generate_reset_token
from realstate_new.utils.views import PublicApi

from .renderers import UserRenderes
from .serializers import ChangePasswordSerializer
from .serializers import GoogleAUthVerifiedData
from .serializers import LoginSerializer
from .serializers import PasswordResetAfterVerificationSerializer
from .serializers import PasswordResetOTPVerifySerializer
from .serializers import PasswordResetSerializer
from .serializers import RedirectLinkSerializer
from .serializers import RegisterSerializer
from .serializers import ResetPasswordSerializer
from .serializers import UserProfileSerializer
from .utils import get_user_role

logger = logging.getLogger(__name__)
User: UserType = get_user_model()


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({"csrf": csrf_token})


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegistrationView(PublicApi):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            subject = "Registration Confirmation"
            recipient_list = [user.email]
            current_site = get_current_site(request)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            related_url = reverse(
                "api:auth:confirm-user",
                kwargs={"uid": uid, "token": token},
            )
            abs_url = f"http://{current_site.domain}{related_url}"
            body = "Thanks for registering with Adoorable.\
                Please click on the link below to verify and activate your account."
            context = {
                "title": "Confirm Account",
                "button_text": "Confirm Account",
                "button_link": abs_url,
                "body": body,
            }
            send_email.delay(
                template_path="emails/base.html",
                recipient_list=recipient_list,
                subject=subject,
                context=context,
            )
            msg = "Registration Successful. Please check your email to verify your account."
            return Response(
                {
                    "msg": msg,
                    "status": True,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(PublicApi):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data["email"]
            password = serializer.data["password"]
            user: UserType | None = authenticate(email=email, password=password)
            if user is not None:
                try:
                    user_group = (Group.objects.get(user=user.id)).name
                except Exception:  # noqa: BLE001
                    user_group = "None"

                token = get_tokens_for_user(user)
                user_role = get_user_role(user)
                data = serializer.validated_data
                if data.get("device_type") and data.get("registration_id"):
                    device = FCMDevice.objects.get_or_create(
                        user=user,
                        device_type=serializer.validated_data["device_type"],
                    )
                    device.registration_id = (serializer.validated_data["registration_id"],)
                    device.save(update_fields=["registration_id"])
                return Response(
                    {
                        "token": token,
                        "msg": "Login Successful",
                        "userid": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "user_status": user_group,
                        "user_role": user_role,
                        "license_info": user.get_required_license_info(),
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"errors": "Please Check Your Username and Password."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"errors": "Incomplete login information provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ProfileView(APIView):
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_calss(
            data=request.data,
            context={"user": request.user},
        )
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "Password changed"})

        return Response(serializer.errors, 400)


class SendPasswordResetOTPView(PublicApi):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            user = User.objects.get(email=serializer.validated_data["email_id"])
            otp = ""
            for _ in range(6):
                otp += str(secrets.randbelow(10))

            # send email
            body = "Please use this OTP to reset your password. This OTP is valid only for 10 mins."
            context = {
                "subject": "OTP Password Reset",
                "title": "OTP for password Reset",
                "button_text": otp,
                "body": body,
            }
            cache.set(
                f"password_reset:{user.id}",
                otp,
                timeout=settings.FORGET_PASSWORD_OTP_TIMEOUT,
            )
            send_email.delay(
                template_path="emails/base.html",
                recipient_list=[user.email],
                subject=context["subject"],
                context=context,
            )
            return Response(
                {"msg": "OTP sent"},
                status=status.HTTP_200_OK,
            )


class PasswordResetOTPVerifyView(PublicApi):
    serializer_class = PasswordResetOTPVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            user = User.objects.get(email=serializer.validated_data["email_id"])
            token = generate_reset_token(user=user)

            return Response(
                {
                    "status": True,
                    "token": token,
                },
                200,
            )


class PasswordResetView(APIView):
    renderer_classes = [UserRenderes]

    def post(self, request, uid, token):
        serializer = ResetPasswordSerializer(
            data=request.data,
        )
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            return Response(
                {"msg": "password reset successfully"},
                status=status.HTTP_200_OK,
            )


class PasswordResetAfterVerificationView(PublicApi):
    def post(self, request):
        serializer = PasswordResetAfterVerificationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            serializer.save()
            return Response({"msg": "Password has been reset successfully."})


class RedirectLinkView(APIView):
    def post(self, request, uid, token):
        try:
            serializer = RedirectLinkSerializer(
                data=request.data,
                context={"uid": uid, "token": token},
            )

            if serializer.is_valid(raise_exception=True):
                return Response(
                    {"msg": "password reset successfully"},
                    status=status.HTTP_200_OK,
                )
        except serializers.ValidationError:
            pass
        return Response(
            {"msg": "password reset failed"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RedirectForm(forms.Form):
    password = forms.CharField(
        label="Password",
        max_length=100,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        max_length=100,
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            msg = "Passwords do not match"
            raise forms.ValidationError(msg)

        return cleaned_data


class UserResetPasswordView(View):
    template_name = "emails/your_template.html"

    def get_user(self, uid, token):
        try:
            id = smart_str(urlsafe_base64_decode(uid))  # noqa: A001
            return get_user_model().objects.get(id=id)
        except (get_user_model().DoesNotExist, DjangoUnicodeDecodeError):
            return None

    def get(self, request, uid, token):
        user = self.get_user(uid, token)

        if user and PasswordResetTokenGenerator().check_token(user, token):
            context = {"uid": uid, "token": token}
            return render(request, self.template_name, context)
        return HttpResponse("Your Reset link has Expired")

    def post(self, request, uid, token):
        user = self.get_user(uid, token)

        if user and PasswordResetTokenGenerator().check_token(user, token):
            password = request.POST.get("password")
            password2 = request.POST.get("password2")

            if password != password2:
                context = {
                    "uid": uid,
                    "token": token,
                    "error_message": "Passwords do not match",
                }
                return render(request, self.template_name, context)
            user.set_password(password)
            user.save()
            return redirect("/login")
        return HttpResponse("Your Reset link has Expired")


def logout_view(request):
    """
    This will be `/api/logout/` on `urls.py`
    """
    logout(request)
    return JsonResponse({"detail": "Success"})


@require_POST
def login_view(request):
    """
    This will be `/api/login/` on `urls.py`
    """
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")
    if username is None or password is None:
        return JsonResponse(
            {"errors": {"__all__": "Please enter both username and password"}},
            status=400,
        )
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"detail": "Success"})
    return JsonResponse(
        {"detail": "Invalid credentials"},
        status=400,
    )


class CheckAuth(APIView):
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        if request.user and request.user.is_authenticated:
            return Response({"detail": "You're Authenticated"})

        return Response({"detail": "You're not Authenticated"})


def confirm_user(request, uid, token):
    try:
        user_id = force_bytes(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)

    except Exception:  # noqa: BLE001
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        context = {
            "title": "Account Verified Successfully.",
            "body": "Thank you for Verifying your Email. You can close this window now.",
        }
        return render(request, "emails/base.html", context=context)

    return JsonResponse("some error occured", safe=False)


class SaveToken(PublicApi):
    def get(self, request, *args, **kwargs):
        rand_id = ""
        for _ in range(10):
            rand_id += str(random.randint(1, 9))  # noqa: S311

        state_token = get_token(request)
        cache.set(rand_id, state_token, 60 * 5)
        return Response(f"{rand_id}-{state_token}", 200)


def state_token(request):
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=777985082123-96jf0j19a69tgbm5gcpso61q19rl31d2.apps.googleusercontent.com&scope=email profile&redirect_uri=http://localhost:8000/api/google/&state={'state'}",  # noqa: E501
    )


class GoogleVerificationView(PublicApi):
    serializer_class = GoogleAUthVerifiedData

    def post(self, request, *args, **kwargs):
        serializer = GoogleAUthVerifiedData(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user: UserType = serializer.save()
            token = get_tokens_for_user(user)
            user_role = get_user_role(user)
            try:
                user_group = (Group.objects.get(user=user.id)).name
            except Exception:  # noqa: BLE001
                user_group = "None"
            data = serializer.validated_data
            if data.get("device_type") and data.get("registration_id"):
                device = FCMDevice.objects.get_or_create(
                    user=user,
                    device_type=serializer.validated_data["device_type"],
                )
                device.count = (serializer.validated_data["registration_id"],)
                device.save(update_fields=["registration_id"])
            return Response(
                {
                    "status": True,
                    "token": token,
                    "msg": "Login Successful",
                    "userid": user.id,
                    "user_status": user_group,
                    "user_role": user_role,
                    "license_info": user.get_required_license_info(),
                },
                status=200,
            )
        return None
