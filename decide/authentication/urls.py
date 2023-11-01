from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LoginView, LogoutView, RegisterView

urlpatterns = [
    path("login/", obtain_auth_token),
    path("signin/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("getuser/", GetUserView.as_view()),
    path("register/", RegisterView.as_view()),
]
