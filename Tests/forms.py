from Main.validators import CharValidator
from django import forms
from django.core.validators import MaxLengthValidator

class TestForm(forms.Form):
    title = forms.CharField(
        label = "Название", 
        widget = forms.TextInput(
            attrs = { "class": "form-control",
                       "placeholder": "Тест" }),
        validators = [
            MaxLengthValidator(50, message = "Максимальное число символов: 50"),
            CharValidator()
        ])

    description = forms.CharField(
        label = "Описание",
        widget = forms.Textarea(attrs = 
                                { "class": "form-control",
                                "placeholder": "Этот тест проверит..." }),
        validators = [
            MaxLengthValidator(2000, message = "Максимальное число символов: 200"),
            CharValidator()
        ])