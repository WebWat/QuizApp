from django import forms
    
class TestForm(forms.Form):
    title = forms.CharField(label = "Название")
    description = forms.CharField(label = "Описание")

class QuestionForm(forms.Form):
    issue = forms.CharField(label = "Текст вопроса")
    choices = ( 
        ("0", "Одиночный"), 
        ("1", "Множественный"),      
    ) 
    choice_type = forms.ChoiceField(choices = choices, label = "Тип ответа")

class EditQuestionForm(forms.Form):
    issue = forms.CharField(label = "Текст вопроса")

class AnswerForm(forms.Form):
    text = forms.CharField(label = "Текст ответа")