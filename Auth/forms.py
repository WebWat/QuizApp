from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms

class CustomLoginForm(forms.Form):
    username = forms.CharField(label = "Логин",
                               widget = forms.TextInput(attrs = 
                                                        { "class": "form-control" }))
    password = forms.CharField(label = "Пароль",
                               widget = forms.PasswordInput(attrs = 
                                                            { "class": "form-control" }))

class RegisterForm(UserCreationForm):
    username = forms.CharField(label = "Логин",
        widget = forms.TextInput(attrs = { "class": "form-control" }))
    password1 = forms.CharField(label = "Пароль",
        widget = forms.PasswordInput(attrs = { "class": "form-control" }))
    password2 = forms.CharField(label = "Повторите пароль",
        widget = forms.PasswordInput(attrs = { "class": "form-control" }))

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label = "Старый пароль",
        widget = forms.PasswordInput(attrs = { "class": "form-control" }))
    new_password1 = forms.CharField(label = "Новый пароль",
        widget = forms.PasswordInput(attrs = { "class": "form-control" }))
    new_password2 = forms.CharField(label = "Повторите новый пароль",
        widget = forms.PasswordInput(attrs = { "class": "form-control" }))
    
class LoginChangeForm(forms.Form):
    username = forms.CharField(label = "Новый логин",
                               widget = forms.TextInput(attrs = 
                                                        { "class": "form-control" }))