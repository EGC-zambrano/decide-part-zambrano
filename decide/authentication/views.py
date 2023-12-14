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

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import PasswordResetTokenGenerator


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
    success_url = "/password_reset/done/"

    def post(self, request):
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            mailMessage = Mail(
                from_email="decidezambrano@gmail.com",
                to_emails=email,
            )

            user = User.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)

            idEncode = f"salt{user.pk}"
            encoded = base64.b64encode(bytes(idEncode, encoding="utf-8")).decode(
                "utf-8"
            )
            urlVerificar = (
                f"{Site.objects.get_current().domain}/reset/{encoded}/{token}/"
            )

            mailMessage.dynamic_template_data = {
                "urlVerificar": urlVerificar,
                "user": user.first_name,
            }
            mailMessage.template_id = "d-01c8e3b0691044009b4512599cf77eca"
            try:
                sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
                sg.send(mailMessage)
            except Exception as e:
                print(e)

            return render(
                request, "authentication/password_reset_done.html", {"form": form}
            )

        else:
            msg = "No user with that email"
            return render(
                request,
                "authentication/password_reset.html",
                {"form": form, "message": msg},
            )


class ResetPasswordDoneView(PasswordResetDoneView):
    template_name = "authentication/password_reset_done.html"
    success_url = "/"


class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = "authentication/password_reset_confirm.html"
    success_url = "/reset/done/"

    def post(self, request):
        form = SetPasswordForm(request.POST)

        new_password = request.POST.get("new_password1", None)
        confirm_new_password = request.POST.get("new_password2", None)
        print(new_password)
        print(confirm_new_password)
        if new_password:
            if new_password == confirm_new_password:
                request.user.set_password(new_password)
                request.user.save()
                return render(
                    request,
                    "authentication/password_reset_complete.html",
                    {"form": form},
                )
            else:
                msg = "Las contraseñas no coinciden."
                return render(
                    request,
                    "authentication/password_reset_complete.html",
                    {"form": form, "message": msg},
                )


class ResetPasswordCompleteView(PasswordResetCompleteView):
    template_name = "authentication/password_reset_complete.html"
    success_url = "/"
