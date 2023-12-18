from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    GetUserView,
    LoginView,
    LogoutView,
    RegisterView,
    ChangePasswordView,
    ResetPasswordView,
    EmailView,
)

from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("login/", obtain_auth_token),
    path("signin/", LoginView.as_view(), name="signin"),
    path("logout/", LogoutView.as_view()),
    path("getuser/", GetUserView.as_view()),
    path("accounts/", include("allauth.urls")),
    path("register/", RegisterView.as_view(), name="register"),
    path("verificar/<str:user_encode>/", EmailView.emailCheck),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "password_reset/",
        ResetPasswordView.as_view(template_name="authentication/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password_reset_done/",
        PasswordResetDoneView.as_view(
            template_name="authentication/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="authentication/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        PasswordResetCompleteView.as_view(
            template_name="authentication/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("social-auth/", include("social_django.urls", namespace="social_auth")),
]
