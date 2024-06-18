from rest_framework import serializers
from thecart_auth.models import User, Profile
from dj_rest_auth.serializers import PasswordResetSerializer
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from rest_framework_simplejwt.settings import api_settings
from calendar import timegm

try:
    from allauth.account import app_settings as allauth_settings
    # from allauth.account.utils import email_address_exists
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer class for a user profile instance
    """

    class Meta:
        fields = "__all__"
        model = Profile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class for a User instance
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "profile",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "phone",
            "is_active",
            "is_deleted",
            "is_regular_user",
            "full_name",
            "is_ops_admin",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "full_name")

    def create(self, validated_data):
        new_user = User.objects.create(**validated_data)
        new_user.set_password(validated_data.get("password"))
        new_user.save()
        return new_user

    def update(self, instance, validated_data):
        profile = validated_data.pop("profile", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if profile is not None:
            user_profile = instance.profile
            for field, value in profile.items():
                setattr(user_profile, field, value)
                user_profile.save()
        instance.save()
        return instance


def jwt_payload_handler(user):
    """
    Custom payload handler
    Token encrypts the dictionary returned by this function, and can be decoded by rest_framework_jwt.utils.jwt_decode_handler
    """
    payload = {
        "user_id": str(user.pk),
        "username": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_rider": user.is_rider,
        "is_ops_admin": user.is_ops_admin,
        "is_regular_user": user.is_regular_user,
        "exp": datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA,
    }

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload["orig_iat"] = timegm(datetime.utcnow().utctimetuple())
    return payload


def jwt_response_payload_handler(token, user=None, request=None):
    return {"token": token}


class BaseRegisterSerializer(serializers.Serializer):
    """
    Implement the RegisterSerializer class to perform custom registration.
    - Create a user Profile and remove the username field.
    - Also set password fields to not required to allow inviting users
    with unusable passwords.
    """

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address.")
                )
        return email

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class RegisterNonAdminUserSerializer(BaseRegisterSerializer):
    """
    Implement the RegisterSerializer class to perform registration
    of a user by an admin user.
    - Create a user Profile and remove the username field.
    - Also set password fields to unusable passwords.
    """

    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def custom_signup(self, request, user):
        Profile.objects.create(user=user,)

    def get_cleaned_data(self):
        return {
            "first_name": self.validated_data.get("first_name"),
            "last_name": self.validated_data.get("last_name"),
            "email": self.validated_data.get("email"),
            "phone": self.validated_data.get("phone"),
            "role": self.validated_data.get("role"),
            "password1": self.validated_data.get("password1"),
        }

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )
        return data


class CustomJWTSerializer(serializers.Serializer):
    """
    Custom Serializer for JWT authentication.
    Re-implements the default JWTSerializer without user field.
    """

    token = serializers.CharField()


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        """
        Return a dictionary of email options
        """
        return {
            "use_https": True,
            "subject_template_name": "registration/password_reset_subject.txt",
            "html_email_template_name": "registration/password_reset_email.html",
            "from_email": "Thecart Accounts <kmathew201@gmail.com",
        }
