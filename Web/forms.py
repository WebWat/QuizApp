from django import forms
    
class TestForm(forms.Form):
    title = forms.CharField(label = "Название")
    description = forms.CharField(label = "Описание")

class QuestionForm(forms.Form):
    issue = forms.CharField(label = "Текст вопроса")
    choices =( 
        ("0", "Одиночный"), 
        ("1", "Множественный"), 
    ) 
    choice_type = forms.ChoiceField(choices = choices, label = "Тип ответа")

class SingleAnswerForm(forms.Form):
    text = forms.CharField(label = "Текст ответа")

class MultipleAnswerForm(forms.Form):
    text = forms.CharField(label = "Текст ответа")
    choices =( 
        ("0", "Не верный"), 
        ("1", "Верный"), 
    ) 
    is_correct = forms.ChoiceField(choices = choices, label = "Это верный ответ?")