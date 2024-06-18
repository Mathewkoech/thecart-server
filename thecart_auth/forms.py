from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class CustomPasswordResetForm(PasswordResetForm):
    """
    Override PasswordResetForm to allow resetting of passwords for unusable users.
    This happens if they verified their emails but failed to continue with setting a password.
    """

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = UserModel._default_manager.filter(**{
            '%s__iexact' % UserModel.get_email_field_name(): email,
            'is_active': True,
        })
        return active_users