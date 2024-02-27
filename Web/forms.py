from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomLoginForm(forms.Form):
    username = forms.CharField(  
        widget = forms.TextInput(attrs={"placeholder": "Логин"}))
    password = forms.CharField(
        widget = forms.PasswordInput(attrs={"placeholder": "Пароль"}))

class RegisterForm(UserCreationForm):
    username = forms.CharField(  
        widget = forms.TextInput(attrs={"placeholder": "Логин"}))
    password1 = forms.CharField(
        widget = forms.PasswordInput(attrs={"placeholder": "Пароль"}))
    password2 = forms.CharField(
        widget = forms.PasswordInput(attrs={"placeholder": "Повторите пароль"}))
    
    # class Meta:
    #     model = User
    #     fields = ["username", "password1", "password2"]
