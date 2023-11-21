from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
import base64
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import EmailCheck
from .forms import LoginForm, RegisterForm
from .serializers import UserSerializer
from django.shortcuts import render, redirect
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
            
            mailMessage = Mail(
                from_email='decidezambrano@gmail.com',
                to_emails=form.cleaned_data.get("email"),
                )
            usernameToEncode = f'{form.cleaned_data.get("username")}'
            encoded = base64.b64encode(bytes(usernameToEncode, encoding='utf-8')).decode('utf-8')
            urlVerificar =f"{request.build_absolute_uri()}verificar/{encoded}"
            mailMessage.dynamic_template_data = {"urlVerificar":urlVerificar}
            mailMessage.template_id = "d-e468c8fe83504fa981029f794ae02c4e"
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                sg.send(mailMessage)
            except Exception as e:
                print(e)
            form.save()
            userToCheck = User.objects.get(username=usernameToEncode)
            emailCheck = EmailCheck(user=userToCheck, emailChecked=False)
            emailCheck.save()
            return redirect("/signin")
        else:
            return render(request, "authentication/register.html", {"form": form})
    def get(self, request):
        form = RegisterForm(None)

        return render(
            request, "authentication/register.html", {"form": form, "msg": None}
        )
class EmailView(TemplateView):
    def emailCheck(self, **kwargs):
        encoded = kwargs.get("user_encode", 0)
        print(self.user.username)
        print(base64.b64decode(str(encoded)).decode('utf-8'))
        if self.user.username == base64.b64decode(str(encoded)).decode('utf-8'):
            checkToAdd =EmailCheck.objects.get(user=self.user)
            print(checkToAdd.user.username)
            checkToAdd.emailChecked=True
            checkToAdd.save()
        return redirect("/")


class ChangePasswordView(PasswordChangeView):
    template_name = "authentication/change_password.html"
    success_url = "/"
