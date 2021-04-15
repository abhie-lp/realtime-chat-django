"""URL mappings for account app"""

from django.urls import path
from .views import account_view

app_name = "account"

urlpatterns = [
    path("<str:username>/", account_view, name="view"),
]
