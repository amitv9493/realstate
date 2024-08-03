import json
import logging
import random

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
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_bytes
from django.utils.encoding import smart_str
from django.utils.html import strip_tags
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

from realstate_new.utils.views import PublicApi

from .renderers import UserRenderes
from .serializers import ChangePasswordSerializer
from .serializers import GoogleAUthVerifiedData
from .serializers import LoginSerializer
from .serializers import PasswordResetSerializer
from .serializers import RedirectLinkSerializer
from .serializers import RegisterSerializer
from .serializers import ResetPasswordSerializer
from .serializers import UserProfileSerializer
from .utils import get_user_role

logger = logging.getLogger(__name__)
User = get_user_model()


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
            message = "Thank you for registering!"
            recipient_list = [user.email]
            current_site = get_current_site(request)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            context = {
                "domain": current_site.domain,
                "uid": uid,
                "token": token,
            }
            from_email = settings.EMAIL_HOST_USER
            html_message = render_to_string(
                "emails/email-verification.html",
                context=context,
            )
            plain_message = strip_tags(html_message)

            message = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=recipient_list,
            )

            message.attach_alternative(html_message, "text/html")
            message.send()
            msg = "Registration Successfull, Please Check Your Mail For Verification"
            return Response(
                {
                    "msg": msg,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(PublicApi):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.data.get("username")
            password = serializer.data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                try:
                    user_group = (Group.objects.get(user=user.id)).name
                except Exception:  # noqa: BLE001
                    user_group = "None"

                token = get_tokens_for_user(user)
                user_role = get_user_role(user)

                return Response(
                    {
                        "token": token,
                        "msg": "Login Successful",
                        "userid": user.id,
                        "user_status": user_group,
                        "user_role": user_role,
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


class SendPasswordResetView(PublicApi):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": self.request},
        )
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            return Response(
                {"msg": "Password reset link is sent if it is registered"},
                status=status.HTTP_200_OK,
            )


class PasswordResetView(APIView):
    renderer_classes = [UserRenderes]

    def post(self, request, uid, token):
        serializer = ResetPasswordSerializer(
            data=request.data,
            context={"uid": uid, "token": token, "request": self.request},
        )
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            return Response(
                {"msg": "password reset successfully"},
                status=status.HTTP_200_OK,
            )


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
        link = f"http://{get_current_site(request).domain}/login"
        user.save(update_fields=["is_active"])

        return render(request, "emails/account-active.html", context={"link": link})

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
            user = serializer.save()
            token = get_tokens_for_user(user)
            user_role = get_user_role(user)
            try:
                user_group = (Group.objects.get(user=user.id)).name
            except Exception:  # noqa: BLE001
                user_group = "None"

            return Response(
                {
                    "token": token,
                    "msg": "Login Successful",
                    "userid": user.id,
                    "user_status": user_group,
                    "user_role": user_role,
                },
                status=200,
            )
        return None
