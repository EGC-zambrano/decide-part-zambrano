from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    GetUserView,
    LoginView,
    LogoutView,
    RegisterView,
    ChangePasswordView,
    ResetPasswordView,
    ResetPasswordDoneView,
    ResetPasswordConfirmView,
    ResetPasswordCompleteView,
)

urlpatterns = [
    path("login/", obtain_auth_token),
    path("signin/", LoginView.as_view(), name="signin"),
    path("logout/", LogoutView.as_view()),
    path("getuser/", GetUserView.as_view()),
    path("accounts/", include("allauth.urls")),
    path("register/", RegisterView.as_view(), name="register"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("password_reset/", ResetPasswordView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        ResetPasswordDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        ResetPasswordConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        ResetPasswordCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("social-auth/", include("social_django.urls", namespace="social_auth")),
]
