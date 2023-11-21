from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LoginView, LogoutView, RegisterView, ChangePasswordView ,EmailView

urlpatterns = [
    path("login/", obtain_auth_token),
    path("signin/", LoginView.as_view(), name="signin"),
    path("logout/", LogoutView.as_view()),
    path("getuser/", GetUserView.as_view()),
    path("accounts/", include("allauth.urls")),
    path("register/", RegisterView.as_view(), name="register"),
    path("register/verificar/<str:user_encode>/", EmailView.emailCheck),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
