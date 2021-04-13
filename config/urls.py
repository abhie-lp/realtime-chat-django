from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

from account.views import register_view, login_view, logout_view
from personal.views import home_screen_view

urlpatterns = [
    path("reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="account/password-change/password_reset_complete.html"
    ), name="password_reset_complete"),
    path("password-reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="account/password-change/password_reset_done.html"
    ), name="password_reset_done"),
    path("password-change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="account/password-change/password_change_done.html"
    ), name="password_change_done"),
    path("register/", register_view, name="register"),
    path("password-reset/", auth_views.PasswordResetView.as_view(),
         name="password_reset"),
    path("password-change/", auth_views.PasswordChangeView.as_view(
        template_name="account/password-change/password_change.html"
    ), name="password_change"),
    path("logout/", logout_view, name="logout"),
    path("login/", login_view, name="login"),
    path('admin/', admin.site.urls),
    path("", home_screen_view, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
