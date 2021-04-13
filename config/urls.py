from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from account.views import register_view, login_view, logout_view
from personal.views import home_screen_view

urlpatterns = [
    path("register/", register_view, name="register"),
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
