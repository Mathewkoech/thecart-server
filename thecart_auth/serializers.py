from rest_framework import serializers,  exceptions
from thecart_auth.models import User, Profile
from dj_rest_auth.serializers import PasswordResetSerializer
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from thecart_auth.forms import CustomPasswordResetForm
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.forms import SetPasswordForm
from calendar import timegm
UserModel = get_user_model()
from django.db.models import Q

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

class ReadProfileSerializer(serializers.ModelSerializer):
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
            "username",
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
        # "is_ops_admin": user.is_ops_admin,
        "is_regular_user": user.is_regular_user,
        "usable": user.usable,
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
    username = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        email_count = User.objects.filter(email__iexact=email).count()
        if email_count > 0:
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address.")
            )
        return email

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        username_count = User.objects.filter(username=username).count()
        if username_count > 0:
            raise serializers.ValidationError(
                _("A user is already registered with this username.")
            )
        return username

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user

class ReadUserSerializer(serializers.ModelSerializer):
    """
    Serializer class for a User instance
    """
    profile = ReadProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "profile",
            "first_name",
            "last_name",
            "full_name",
            "username",
            "role",
            "usable",
            "phone",
            "is_active",
            "is_deleted",
            "is_ops_admin",
            "is_superuser",
            "_is_rider",
            "_is_regular_user",
            "full_name"
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "full_name")

class CustomPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    user_id = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())

    set_password_form_class = SetPasswordForm

    set_password_form = None

    def __init__(self, *args, **kwargs):
        print(self)
        self.old_password_field_enabled = getattr(
            settings, 'OLD_PASSWORD_FIELD_ENABLED', False,
        )
        self.logout_on_password_change = getattr(
            settings, 'LOGOUT_ON_PASSWORD_CHANGE', False,
        )
        super().__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')

        self.user_id = self.request.data.get("user_id", None)
        if self.user_id is not None:
            user = User.objects.get(pk=self.user_id)
        self.user = getattr(self.request, 'user', user)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            err_msg = _('Your old password was entered incorrectly. Please enter it again.')
            raise serializers.ValidationError(err_msg)
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs,
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)
class CustomRegisterSerializer(BaseRegisterSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def custom_signup(self, request, user):
        Profile.objects.create(
            user=user, created_by=user
        )
        user.is_ops_admin = True
        user.save()

    def get_cleaned_data(self):
        return {
            "first_name": self.validated_data.get("first_name"),
            "last_name": self.validated_data.get("last_name"),
            "phone": self.validated_data.get("phone"),
            "password1": self.validated_data.get("password1"),
            "email": self.validated_data.get("email"),
            "username": self.validated_data.get("username"),
        }



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
        role = self.validated_data.get("role")
        user.role = role
        user.save()
        Profile.objects.create(user=user, created_by=user)


    def get_cleaned_data(self):
        return {
            "first_name": self.validated_data.get("first_name"),
            "last_name": self.validated_data.get("last_name"),
            "email": self.validated_data.get("email"),
            "phone": self.validated_data.get("phone"),
            "username":self.validated_data.get("username"),
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

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        # Custom data you want to include
        # data.update({'user': self.user.username})
        # data.update({'id': self.user.id})
        # and everything else you want to send in the response
        return data

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


class CustomAuthenticationBackend:

    def authenticate(self, email_or_username=None, password=None):
        try:
             user = User.objects.get(
                 Q(email__iexact=email_or_username) | Q(username__iexact=email_or_username)
             )
             pwd_valid = user.check_password(password)
             if pwd_valid:            
                 return user
             return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class CustomLoginSerializer(serializers.Serializer):
    username_email = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = authenticate(email=email, password=password)
        else:
            msg = _('Must include "email/username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_phone(self, phone, password):
        user = None

        if phone and password:
            user = authenticate(phone=phone, password=password)
        else:
            msg = _('Must include "phone" and "password".')
            raise exceptions.ValidationError(msg)

        return user


    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = authenticate(email=email, password=password)
        elif username and password:
            user = authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email_override(self, username_email, password):
        user = None

        if username_email and password:
            user = CustomAuthenticationBackend.authenticate(self, email_or_username=username_email, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username_email = attrs.get('username_email')
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email_override(username_email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs
