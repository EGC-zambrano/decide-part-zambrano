from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from .views import (
    PasswordResetRequestView,
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
    path("password_reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("social-auth/", include("social_django.urls", namespace="social_auth")),
]
