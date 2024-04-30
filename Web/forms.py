from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator

class CharValidator:
    ALLOWED_CHARS = ("ЁЙФЯЦЧУВСКАМЕПИНРТГОШЛЩДЗЖХЭёйфяцычувскамепинртгоьшлбщдюзжхэъ"
                     "QAZWSXEDCRFVTGBYHNUJMIKOLPqazwsxedcrfvtgbyhnujmikolp"
                     "1234567890-_.,!~:;№=+*/%()? \r\n\t")
    def __init__(self, message=None):
        self.message = message if message else "Недопустимый символ"
    def __call__(self,value, *args, **kwargs):
        if not (set(value) <= set(self.ALLOWED_CHARS)):
            raise ValidationError(self.message)


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
    image = forms.ImageField(label = "Рисунок", 
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

class AnswerForm(forms.Form):
    text = forms.CharField( label = "Текст ответа",
        widget = forms.TextInput(
            attrs = { "class": "form-control",
                      "placeholder": "Екатеринбург" }),
            validators = [
                MaxLengthValidator(50, message = "Максимальное число символов: 50"),
                CharValidator()
            ])