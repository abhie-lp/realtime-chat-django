from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

from .forms import RegistrationForm


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
