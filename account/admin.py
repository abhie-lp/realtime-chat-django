from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account


@admin.register(Account)
class AccountAdmin(UserAdmin):
    """Configure custom user model"""
    list_display = ("email", "username", "date_joined", "last_login",
                    "is_admin", "is_staff")
    search_fields = ("email", "username")
    readonly_fields = ("id", "date_joined", "last_login")
    fieldsets = ()
    filter_horizontal = ()
    list_filter = ("is_admin", "is_staff", "is_superuser",
                   "last_login", "date_joined")
