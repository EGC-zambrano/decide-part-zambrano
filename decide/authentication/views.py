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
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.views import (
    PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.contrib.auth import update_session_auth_hash
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os
import base64
from django.contrib.auth.models import User


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


class PasswordResetRequestView(FormView):
    template_name = "authentication/password_reset.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("/")  # Replace 'home' with your home page URL name

    def post(self, request):
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")

            user = User.objects.get(email=email)

            mailMessage = Mail(
                from_email="decidezambrano@gmail.com",
                to_emails=email,
            )
            idEncode = f"salt{user.pk}"
            encoded = base64.b64encode(bytes(idEncode, encoding="utf-8")).decode(
                "utf-8"
            )
            urlVerificar = f"{request.build_absolute_uri()}/{encoded}"
            mailMessage.dynamic_template_data = {
                "urlVerificar": urlVerificar,
                "user": user.first_name,
            }
            mailMessage.template_id = "d-01c8e3b0691044009b4512599cf77eca"
            load_dotenv()
            print(os.getenv("SENDGRID_API_KEY"))
            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
            response = sg.send(mailMessage)

    def form_valid(self, form):
        form.save(
            use_https=self.request.is_secure(),
            request=self.request,
        )
        return super().form_valid(form)


def consulta_email(request, **kwargs):
    encoded = kwargs.get("encoded", 0)
    email = request.POST.get("email", None)
    decode = base64.b64decode(str(encoded)).decode("utf-8")
    userId = decode.replace("salt", "")
    user = User.objects.get(pk=userId)
    return render(
        request,
        "authentication/password_reset_confirm.html",
        {"user": user, "hash": encoded},
    )


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    template_name = "password_reset.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy(
        "/signin/"
    )  # Replace 'login' with your login page URL name

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)
