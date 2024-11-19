import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import signing
from django.core.cache import cache
from django.utils import timezone
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework import status
from rest_framework.validators import UniqueValidator

User = get_user_model()  # noqa: F811


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "username", "email"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)
    registration_id = serializers.CharField(required=False)
    device_type = serializers.CharField(required=False)


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=get_user_model().objects.all(),
                message="A user with this email address already exists.",
            ),
        ],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = (
            "password",
            "password2",
            "email",
        )
        extra_kwargs = {
            "first_name": {"required": True, "allow_null": False},
            "last_name": {"required": True, "allow_null": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."},
            )
        return attrs

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data["email"].split("@")[0],
            email=validated_data["email"],
            is_active=False,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(
        max_length=55,
        style={"input_type": "password"},
        write_only=True,
    )
    password = serializers.CharField(
        max_length=55,
        style={"input_type": "password"},
        validators=[validate_password],
        write_only=True,
    )
    password2 = serializers.CharField(
        max_length=55,
        style={"input_type": "password"},
        write_only=True,
    )

    class Meta:
        model = get_user_model()
        fields = ["current_password", "password", "password2"]

    def validate(self, attrs):
        password = attrs["password"]
        password2 = attrs["password2"]
        user = self.context.get("user")
        success = user.check_password(attrs["current_password"])

        if password == password2 and success:
            user.set_password(password)
            user.save()
            return attrs
        msg = "password do not match"
        raise serializers.ValidationError(msg)


class PasswordResetSerializer(serializers.Serializer):
    email_id = serializers.EmailField()

    class Meta:
        fields = ["email_id"]

    def validate(self, attrs):
        email = attrs["email_id"]
        if not User.objects.filter(email=email).exists():
            msg = "This email is not registered!"
            raise serializers.ValidationError(msg)
        return attrs


class PasswordResetOTPVerifySerializer(serializers.Serializer):
    email_id = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    class Meta:
        fields = ["email_id"]

    def validate_email_id(self, value):
        if not User.objects.filter(email=value).exists():
            msg = "This email is not registered!"
            raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs):
        user = User.objects.filter(email=attrs["email_id"])
        otp = attrs["otp"]
        if not user.exists():
            raise serializers.ValidationError({"email_id": "User does not exist."})

        if not (cached_otp := cache.get(f"password_reset:{user[0].id}")) or cached_otp != otp:
            raise serializers.ValidationError({"otp": "OTP is invalid."})

        cache.delete(f"password_reset:{user[0].id}")
        return super().validate(attrs)


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=55,
        style={"input_type": "password"},
        validators=[validate_password],
        write_only=True,
    )
    password2 = serializers.CharField(
        max_length=55,
        style={"input_type": "password"},
        write_only=True,
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        password = attrs["password"]
        password2 = attrs["password2"]
        uid = self.context.get("uid")
        token = self.context.get("token")
        id = smart_str(urlsafe_base64_decode(uid))  # noqa: A001
        user = User.objects.get(id=id)

        try:
            if PasswordResetTokenGenerator().check_token(user, token):
                if password == password2:
                    user.set_password(password)
                    user.save()
                    return attrs
                msg = "password do not match"
                raise serializers.ValidationError(msg)

            msg = "Link is expired or already used!"
            raise serializers.ValidationError(msg)

        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            msg = "Token is not valid or expired."
            raise serializers.ValidationError(msg) from None


class RedirectLinkSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=55,
        style={"input_type": "password"},
        validators=[validate_password],
        write_only=True,
    )
    password2 = serializers.CharField(
        max_length=55,
        style={"input_type": "password"},
        validators=[validate_password],
        write_only=True,
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        password = attrs["password"]
        password2 = attrs["password2"]
        uid = self.context.get("uid")
        token = self.context.get("token")
        id = smart_str(urlsafe_base64_decode(uid))  # noqa: A001
        user = User.objects.get(id=id)

        try:
            if PasswordResetTokenGenerator().check_token(user, token):
                if password == password2:
                    user.set_password(password)
                    user.save()
                    return attrs
                msg = "password do not match"
                raise serializers.ValidationError(msg)

        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            msg = "Token is not valid or expired."
            raise serializers.ValidationError(msg) from None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "first_name"]


class GoogleVerificationSerializer(serializers.Serializer):
    code = serializers.CharField()

    id_token = None

    def validate_code(self, value):
        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET

        data = {
            "code": value,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:8000/api/google/",
        }

        response = requests.post(
            url="https://oauth2.googleapis.com/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )

        if response.status_code == status.HTTP_200_OK:
            self.id_token = response.json()["id_token"]
        else:
            msg = "Code is invalid"
            raise serializers.ValidationError(msg)

    def validate_state_token(self, value):
        id, token = value.split("-")  # noqa: A001
        cached_value = cache.get(id)
        if cached_value != token:
            msg = "csrf validation failed"
            raise serializers.ValidationError(msg)

        cache.delete(id)


class GoogleAUthVerifiedData(serializers.Serializer):
    email = serializers.EmailField()
    family_name = serializers.CharField()
    given_name = serializers.CharField()
    registration_id = serializers.CharField(required=False)
    device_type = serializers.CharField(required=False)

    def create(self, validated_data):
        first_name = validated_data["family_name"]
        last_name = validated_data["given_name"]
        email = validated_data["email"]
        username = email.split("@")[0]
        try:
            user = User.objects.get(
                email=email,
            )
        except User.DoesNotExist:
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
        return user


class PasswordResetAfterVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_token(self, value):
        try:
            data = signing.loads(value, salt="password-reset-salt")
        except signing.BadSignature as e:
            msg = "Invalid token."
            raise serializers.ValidationError(msg) from e

        try:
            timestamp = timezone.datetime.fromisoformat(data["timestamp"])
        except ValueError as e:
            msg = "Invalid timestamp format."
            raise serializers.ValidationError(msg) from e
        if now() > timestamp:
            msg = "Token has expired."
            raise serializers.ValidationError(msg)

        user = User.objects.get(id=data["user_id"])
        if not user:
            msg = "Invalid token."
            raise serializers.ValidationError(msg)

        self.user = user
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance

    def save(self, *args, **kwargs):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
        return self.user
