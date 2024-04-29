from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator


class Validetor_login_password:
    ALLOWED_CHARS = ("ЁЙФЯЦЧУВСКАМЕПИНРТГОШЛЩДЗЖХЭёйфяцычувскамепинртгоьшлбщдюзжхэъ"
                     "QAZWSXEDCRFVTGBYHNUJMIKOLPqazwsxedcrfvtgbyhnujmikolp"
                     "1234567890-_.,!")
    def __init__(self, message=None):
        self.message = message if message else "Допустимые символы: кирилица, латинеца, цифры, -_.,!"
    def __call__(self,value, *args, **kwargs):
        if not (set(value) <= set(self.ALLOWED_CHARS)):
            raise ValidationError(self.message)

class CustomLoginForm(forms.Form):
    username = forms.CharField( label = "Логин",
                                widget = forms.TextInput(attrs = { "class": "form-control" }),
                                validators=[
                                    MinLengthValidator(6, message="Минимальное число символов 6"),
                                    MaxLengthValidator(100, message="Максимальное число символов 100"),
                                    Validetor_login_password(),
                                ],
                                )
    password = forms.CharField( label = "Пароль",
                                widget = forms.PasswordInput(attrs = { "class": "form-control" }),
                                validators=[
                                    MinLengthValidator(8, message="Минимальное число символов 8"),
                                    MaxLengthValidator(100, message="Максимальное число символов 100"),
                                    Validetor_login_password(),
                                ],
                                )

class RegisterForm(UserCreationForm):
    username = forms.CharField( label = "Логин",
                                widget = forms.TextInput(attrs = { "class": "form-control" }),
                                validators=[
                                    MinLengthValidator(6, message="Минимальное число символов 6"),
                                    MaxLengthValidator(100, message="Максимальное число символов 100"),
                                    Validetor_login_password(),
                                ],
                                )
    password1 = forms.CharField(label = "Пароль",
                                widget = forms.PasswordInput(attrs = { "class": "form-control" }),
                                validators=[
                                    MinLengthValidator(8, message="Минимальное число символов 8"),
                                    MaxLengthValidator(100, message="Максимальное число символов 100"),
                                    Validetor_login_password(),
                                ],
                                )
    password2 = forms.CharField(label = "Повторите пароль",
                                widget = forms.PasswordInput(attrs = { "class": "form-control" }),
                                validators=[
                                    MinLengthValidator(8, message="Минимальное число символов 8"),
                                    MaxLengthValidator(100, message="Максимальное число символов 100"),
                                    Validetor_login_password(),
                                ],
                                )

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField( label = "Старый пароль",
                                    widget = forms.PasswordInput(attrs = { "class": "form-control" }),
                                    validators=[
                                        MinLengthValidator(8, message="Минимальное число символов 8"),
                                        MaxLengthValidator(100, message="Максимальное число символов 100"),
                                        Validetor_login_password(),
                                    ],
                                    )
    new_password1 = forms.CharField(label = "Новый пароль",
                                    widget = forms.PasswordInput(attrs = { "class": "form-control" }),
                                    validators=[
                                        MinLengthValidator(8, message="Минимальное число символов 8"),
                                        MaxLengthValidator(100, message="Максимальное число символов 100"),
                                        Validetor_login_password(),
                                    ],
                                    )
    new_password2 = forms.CharField(label = "Повторите новый пароль",
        widget = forms.PasswordInput(attrs = { "class": "form-control" }),
                                validators=[
                                    MinLengthValidator(8, message="Минимальное число символов 8"),
                                    MaxLengthValidator(100, message="Максимальное число символов 100"),
                                    Validetor_login_password(),
                                ],
                                )
    
class LoginChangeForm(forms.Form):
    username = forms.CharField(label = "Новый логин",
                               widget = forms.TextInput(attrs = { "class": "form-control" }),
                                validators=[
                                    MinLengthValidator(6, message="Минимальное число символов 6"),
                                    MaxLengthValidator(100, message="Максимальное число символов 100"),
                                    Validetor_login_password(),
                                ],
                                )