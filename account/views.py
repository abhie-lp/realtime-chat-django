from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import alogin, aauthenticate, alogout
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm, LoginForm, AccountUpdateForm
from .models import Account

from friends.models import FriendRequest, FriendList
from utils.search import binary_search


async def register_view(request):
    """View to register new user"""
    if (user := await request.auser()) and user.is_authenticated:
        return HttpResponse(f"You are already authenticated with {user.email}")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if await sync_to_async(form.is_valid)():
            await sync_to_async(form.save)()
            account = await aauthenticate(
                email=form.cleaned_data["email"].lower(),
                password=form.cleaned_data["password1"],
            )
            if account.is_active:
                await alogin(request, account)
            if request.GET.get("next"):
                return redirect(request.GET.get("next"))
            return redirect("home")
    else:
        form = RegistrationForm()
    return render(request, "account/register.html", {"registration_form": form})


async def logout_view(request):
    """Log out user out of the website"""
    await alogout(request)
    return redirect("home")


async def login_view(request):
    """Login view to authenticate the user using email and password"""
    if (await request.auser()).is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if await sync_to_async(form.is_valid)():
            user = await aauthenticate(
                email=form.cleaned_data["email"], password=form.cleaned_data["password"]
            )
            if user:
                if user.is_active:
                    await alogin(request, user)
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


async def account_view(request, username):
    """View to show details of user account"""
    request.user = await request.auser()
    try:
        account = await Account.objects.aget(username=username)
    except Account.DoesNotExist:
        return HttpResponseNotFound("The user doesn't exist.")
    else:
        request_user = request.user
        is_friend, request_status, friend_requests = False, None, None
        pending_friend_request_id = None

        # Check if client-user is logged-in and is seeing self account
        is_self = request_user.is_authenticated and request_user == account

        if request_user.is_authenticated and not is_self:
            # Check if client user is friend with account opened
            is_friend = await (
                await sync_to_async(lambda: request_user.friend_list)()
            ).is_friend(account)
            if not is_friend:
                # Check if friend request has been sent by any of them
                friend_request: FriendRequest = (
                    await FriendRequest.objects.filter(
                        Q(sender=request_user, receiver=account)
                        | Q(sender=account, receiver=request_user),
                        is_active=True,
                    )
                    .select_related("sender", "receiver")
                    .alast()
                )
                if friend_request:
                    # Check if request is sent by sign-in user to other account
                    if (
                        friend_request.sender == request_user
                        and friend_request.receiver == account
                    ):
                        request_status = "SENT"
                    # Check if request is received by sign-in user from other
                    # account
                    elif (
                        friend_request.sender == account
                        and friend_request.receiver == request_user
                    ):
                        request_status = "RECEIVED"
                    pending_friend_request_id = friend_request.pk
        elif is_self:
            friend_requests = await FriendRequest.objects.filter(
                receiver=request_user, is_active=True
            ).acount()
        ctx = {
            "account": account,
            "is_self": is_self,
            "is_friend": is_friend,
            "request_status": request_status,
            "friends_count": await account.friends.acount(),
            "friend_requests": friend_requests,
            "pending_friend_request_id": pending_friend_request_id,
        }
    return render(request, "account/account.html", ctx)


async def account_search_view(request):
    """View to search accounts"""

    request.user = await request.auser()
    ctx = {}
    search_query = request.GET.get("q")
    if len(search_query) > 0:
        search_results = (
            Account.objects.filter(
                Q(email__icontains=search_query) | Q(username__icontains=search_query)
            )
            .only("id", "email", "username", "profile_image")
            .distinct()
        )

        # [(account1: Account, friendship_status_with_me: bool), ...]
        if request.user.is_authenticated:
            friend_list = await FriendList.objects.select_related("user").aget(user=request.user)
            my_friends = await sync_to_async(tuple)(friend_list.friends.order_by("pk").values_list("pk", flat=True))
            accounts = [
                (account, binary_search(account.pk, my_friends))
                async for account in search_results
            ]
        else:
            accounts = [(account, False) for account in search_results]
        ctx["accounts"] = accounts

    return render(request, "account/account_search.html", ctx)


@login_required()
async def account_update_view(request):
    """View to updated account details"""
    ctx = {"DATA_UPLOAD_MAX_SIZE": settings.DATA_UPLOAD_MAX_MEMORY_SIZE}
    request.user = await request.auser()
    if request.method == "POST":
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if await sync_to_async(form.is_valid)():
            await sync_to_async(form.save)()
            return redirect("account:view", request.user.username)
    else:
        form = AccountUpdateForm(instance=request.user)
    ctx["form"] = form
    return render(request, "account/account_update.html", ctx)
