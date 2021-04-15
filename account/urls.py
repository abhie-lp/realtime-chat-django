"""URL mappings for account app"""

from django.urls import path
from .views import account_view, account_search_view

app_name = "account"

urlpatterns = [
    path("search/", account_search_view, name="search"),
    path("<str:username>/", account_view, name="view"),
]
