from django import forms
from Main.validators import CharValidator
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator

class QuestionForm(forms.Form):
    issue = forms.CharField(
        label = "Текст вопроса", 
        widget = forms.TextInput(attrs = 
                                    { "class": "form-control",
                                      "placeholder": "Какой сегодня день?" }),
        validators = [
            MaxLengthValidator(200, message = "Максимальное число символов: 200"),
            CharValidator()
        ])
    choices = ( 
        ("0", "Одиночный"), 
        ("1", "Множественный"),      
    ) 
    choice_type = forms.ChoiceField(choices = choices, label = "Тип ответа",
        widget = forms.Select(
            attrs = { "class": "form-control",
                      "placeholder": "Какой сегодня день?" }))
    image = forms.ImageField(label = "Рисунок (опционально)", 
        widget = forms.FileInput(attrs = { "class": "form-control" }))
    
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields["image"].required = False


class EditQuestionForm(forms.Form):
    issue = forms.CharField(
        label = "Текст вопроса", 
        widget = forms.TextInput(attrs = { "class": "form-control" }),
        validators = [
            MaxLengthValidator(1000, message = "Максимальное число символов: 1000"),
            CharValidator()
        ])
    image = forms.ImageField(label = "Рисунок", 
        widget = forms.FileInput(attrs = { "class": "form-control" }))
    
    def __init__(self, *args, **kwargs):
        super(EditQuestionForm, self).__init__(*args, **kwargs)
        self.fields["image"].required = False

class AnswerForm(forms.Form):
    text = forms.CharField( label = "Текст ответа",
        widget = forms.TextInput(
            attrs = { "class": "form-control",
                      "placeholder": "Екатеринбург" }),
            validators = [
                MaxLengthValidator(50, message = "Максимальное число символов: 50"),
                CharValidator()
            ])