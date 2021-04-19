"""Handle HTML forms"""

from PIL import Image

from django import forms
from django.contrib.auth.forms import UserCreationForm

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


class AccountUpdateForm(forms.ModelForm):
    """Form to update user account details"""
    x = forms.FloatField(widget=forms.HiddenInput, initial=-1)
    y = forms.FloatField(widget=forms.HiddenInput, initial=-1)
    width = forms.FloatField(widget=forms.HiddenInput, initial=-1)
    height = forms.FloatField(widget=forms.HiddenInput, initial=-1)
    upload_image = forms.IntegerField(widget=forms.HiddenInput, initial=0)

    class Meta:
        model = Account
        fields = ("username", "email", "profile_image", "hide_email")

    def save(self, commit=True):
        """Override save to resized image"""
        account = super(AccountUpdateForm, self).save(commit=commit)
        if self.cleaned_data["upload_image"]:
            x = self.cleaned_data["x"]
            y = self.cleaned_data["y"]
            width = self.cleaned_data["width"]
            height = self.cleaned_data["height"]

            image = Image.open(account.profile_image)
            cropped_image = image.crop((x, y, width + x, height + y))
            cropped_image.save(
                account.profile_image.path, optimize=True, quality=75
            )
        return account
