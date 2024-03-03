from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomLoginForm(forms.Form):
    username = forms.CharField(label = "Логин")
    password = forms.CharField(label = "Пароль",
        widget = forms.PasswordInput())

class RegisterForm(UserCreationForm):
    username = forms.CharField(label = "Логин")
    password1 = forms.CharField(label = "Пароль",
        widget = forms.PasswordInput())
    password2 = forms.CharField(label = "Повторите пароль",
        widget = forms.PasswordInput())