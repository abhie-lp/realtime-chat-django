"""Handle HTML forms"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from account.models import Account


class RegistrationForm(UserCreationForm):
    """Create the registration form"""
    email = forms.EmailField(max_length=255,
                             help_text="Required. Add a valid email.")

    class Meta:
        model = Account
        fields = ("email", "username", "password1", "password2")

    def clean_email(self):
        """Run check on email"""
        email = self.cleaned_data["email"].lower()
        try:
            Account.objects.get(email=email)
        except Account.DoesNotExist:
            return email
        else:
            raise forms.ValidationError(f"Email {email} is already in use.")

    def clean_username(self):
        """Run check on username"""
        username = self.cleaned_data["username"]
        try:
            Account.objects.get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError(f"Username {username} already in use.")


class LoginForm(forms.Form):
    """Create a login form"""
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    email = forms.EmailField(label="Email")
