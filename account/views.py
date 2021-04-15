from django.http import HttpResponse, HttpResponseNotFound
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from .forms import RegistrationForm, LoginForm
from .models import Account


def register_view(request):
    """View to register new user"""
    if request.user.is_authenticated:
        return HttpResponse(
            f"You are already authenticated with {request.user.email}"
        )
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            account = authenticate(email=form.cleaned_data["email"].lower(),
                                   password=form.cleaned_data["password1"])
            if account.is_active:
                login(request, account)
            if request.GET.get("next"):
                return redirect(request.GET.get("next"))
            return redirect("home")
    else:
        form = RegistrationForm()
    return render(request, "account/register.html",
                  {"registration_form": form})


def logout_view(request):
    """Log out user out of the website"""
    logout(request)
    return redirect("home")


def login_view(request):
    """Login view to authenticate the user using email and password"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data["email"],
                                password=form.cleaned_data["password"])
            if user:
                if user.is_active:
                    login(request, user)
                    if request.GET.get("next"):
                        return redirect(request.GET.get("next"))
                    return redirect("home")
                else:
                    form.add_error(None, "User account is not active.")
            else:
                form.add_error(None, "User not found with above credentials")
    else:
        form = LoginForm()
    return render(request, "account/login.html", {"login_form": form})


def account_view(request, username):
    """View to show details of user account"""
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return HttpResponseNotFound("The user doesn't exist.")
    else:
        request_user = request.user
        is_self, is_friend = True, False

        if request_user.is_authenticated and request_user != account:
            is_self = False
        elif not request_user.is_authenticated:
            is_self = False
    return render(request, "account/account.html",
                  {"account": account, "is_self": is_self,
                   "is_friend": is_friend})


def account_search_view(request):
    """View to search accounts"""

    ctx = {}
    if request.method == "GET":
        search_query = request.GET.get("q")
        if len(search_query) > 0:
            search_results = Account.objects.filter(
                Q(email__icontains=search_query),
                Q(username__icontains=search_query)
            ).only("id", "email", "username", "profile_image").distinct()

            # [(account1: Account, friend_or_not: bool), ...]
            accounts = [(account, False) for account in search_results]
            ctx["accounts"] = accounts

    return render(request, "account/account_search.html", ctx)
