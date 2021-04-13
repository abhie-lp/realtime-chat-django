from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from .forms import RegistrationForm, LoginForm


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
