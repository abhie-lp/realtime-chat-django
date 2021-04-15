from os import path

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin


class MyAccountManager(BaseUserManager):
    """Manager for custom user model"""

    def create_user(self, email, username, password=None):
        """Create new user"""
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        user = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """Create a new superuser"""
        user = self.create_user(email, username, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


def get_profile_image_filepath(self, _):
    """Return the profile image path for the user"""
    return f"profile_images/{self.pk}/profile_image.png"


def get_default_profile_image():
    """Return the path  of default profile image"""
    return "defaults/logo.jpg"


class Account(AbstractBaseUser):
    """Model for user"""
    email = models.EmailField("email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField("date_joined", auto_now_add=True)
    last_login = models.DateTimeField("last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_image = models.ImageField(
        max_length=255,  null=True, blank=True,
        upload_to=get_profile_image_filepath,
        default=get_default_profile_image
    )
    hide_email = models.BooleanField(default=True)

    objects = MyAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_profile_image_filename(self):
        """Return the filename from the complete path of profile image"""
        return path.basename(self.profile_image.name)

    def has_perm(self, *_):
        """For checking permissions. to keep it simple
        all admin have ALL permissons"""
        return self.is_admin

    @staticmethod
    def has_module_perms(_):
        """Does this user have permission to view this app?
        (ALWAYS YES FOR SIMPLICITY)"""
        return True
