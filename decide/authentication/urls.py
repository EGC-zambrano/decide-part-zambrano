from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from .views import (
    GetUserView,
    LoginView,
    LogoutView,
    RegisterView,
    ChangePasswordView,
)

urlpatterns = [
    path("login/", obtain_auth_token),
    path("signin/", LoginView.as_view(), name="signin"),
    path("logout/", LogoutView.as_view()),
    path("getuser/", GetUserView.as_view()),
    path("accounts/", include("allauth.urls")),
    path("register/", RegisterView.as_view(), name="register"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "restore-password/",
        PasswordResetView.as_view(template_name="authentication/password_reset.html"),
        name="password_reset",
    ),
    path(
        "restore-password/done/",
        PasswordResetDoneView.as_view(
            template_name="authentication/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="authentication/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="authentication/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
