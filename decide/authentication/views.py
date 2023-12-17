import os
import base64
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import LoginForm, RegisterForm
from .serializers import UserSerializer

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import (
    PasswordResetView,
)


# Non-api view
class LoginView(TemplateView):
    def post(self, request):
        form = LoginForm(request.POST)

        msg = None

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)

                next_url = request.GET.get("next", None)
                if next_url:
                    return redirect(next_url)
                return redirect("/")
            else:
                msg = "Credenciales incorrectas"
        else:
            msg = "Error en el formulario"

        return render(request, "authentication/login.html", {"form": form, "msg": msg})

    def get(self, request):
        form = LoginForm(None)

        return render(request, "authentication/login.html", {"form": form, "msg": None})


class GetUserView(APIView):
    def post(self, request):
        key = request.data.get("token", "")
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(TemplateView):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect("/")


class RegisterView(APIView):
    def post(self, request):
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("/signin")
        else:
            return render(request, "authentication/register.html", {"form": form})

    def get(self, request):
        form = RegisterForm(None)

        return render(
            request, "authentication/register.html", {"form": form, "msg": None}
        )


class ChangePasswordView(PasswordChangeView):
    template_name = "authentication/change_password.html"
    success_url = "/"


class ResetPasswordView(PasswordResetView):
    template_name = "authentication/password_reset.html"

    def post(self, request):
        form = PasswordResetForm(request.POST)

        ## TODO: Check that email is in database before sending to user
