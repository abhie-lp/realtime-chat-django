"""Handle the functionality when user tries to authenticate"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()
CASE_INSENSITIVE_USERNAME_FIELD = "{}__iexact".format(UserModel.USERNAME_FIELD)


class CaseInsensitiveModelBackend(ModelBackend):
    """Backend to authenticate using email without case-insensitive"""

    async def aauthenticate(self, request, username=None, password=None, **kwargs):
        """Perform checks to authenticate"""
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = await UserModel._default_manager.aget(
                **{CASE_INSENSITIVE_USERNAME_FIELD: username}
            )
        except UserModel.DoesNotExist:
            return
        else:
            if (await user.acheck_password(password)) and self.user_can_authenticate(
                user
            ):
                return user
