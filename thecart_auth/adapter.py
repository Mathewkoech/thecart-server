from allauth.account.adapter import DefaultAccountAdapter
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from allauth.account.utils import user_email, user_field

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom Adapter that overrides the send_confirmation_mail method to add custom context
    """

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        data = form.cleaned_data
        user_email(user, data.get('email'))
        user.username = data.get('username')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.phone = data.get('phone')
        user.role = data.get('role')

        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        
        if commit:
            user.save()
        return user

    def clean_email(self, email):
        """
        Normalize the email address by lowercasing it.
        """
        return email.lower()

    def respond_email_verification_sent(self, request, user):
        return HttpResponseRedirect(reverse("auth:account_email_verification_sent"))
