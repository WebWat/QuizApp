from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
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

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label = "Старый пароль",
        widget = forms.PasswordInput())
    new_password1 = forms.CharField(label = "Новый пароль",
        widget = forms.PasswordInput())
    new_password2 = forms.CharField(label = "Повторите новый пароль",
        widget = forms.PasswordInput())
    
class LoginChangeForm(forms.Form):
    username = forms.CharField(label = "Новый логин")