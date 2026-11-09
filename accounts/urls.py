from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import path, reverse_lazy

from . import views
from .forms import SamsAuthenticationForm

app_name = "accounts"


class SamsPasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:password_change_done")


class SamsPasswordChangeDoneView(
    LoginRequiredMixin,
    auth_views.PasswordChangeDoneView,
):
    template_name = "accounts/password_change_done.html"


urlpatterns = [
    path("", views.home, name="home"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=SamsAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password/change/",
        SamsPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password/change/done/",
        SamsPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
]
