from django import forms
    
class TestForm(forms.Form):
    title = forms.CharField(label = "Название", 
                            widget = forms.TextInput(attrs = 
                                                     { "class": "form-control",
                                                       "placeholder": "Тест" }))
    description = forms.CharField(label = "Описание",
                                  widget = forms.Textarea(attrs = 
                                                          { "class": "form-control",
                                                            "placeholder": "Этот тест проверит..." }))

class QuestionForm(forms.Form):
    issue = forms.CharField(label = "Текст вопроса", 
                            widget = forms.TextInput(attrs = 
                                                     { "class": "form-control",
                                                       "placeholder": "Какой сегодня день?" }))
    choices = ( 
        ("0", "Одиночный"), 
        ("1", "Множественный"),      
    ) 
    choice_type = forms.ChoiceField(choices = choices, label = "Тип ответа",
                                    widget = forms.Select(attrs = 
                                                          { "class": "form-control",
                                                            "placeholder": "Какой сегодня день?" }))
    image = forms.ImageField(label = "Рисунок", 
                             widget = forms.FileInput(attrs = 
                                                     { "class": "form-control" }))

class EditQuestionForm(forms.Form):
    issue = forms.CharField(label = "Текст вопроса", 
                            widget = forms.TextInput(attrs = { "class": "form-control" }))

class AnswerForm(forms.Form):
    text = forms.CharField(label = "Текст ответа",
                           widget = forms.TextInput(attrs = { "class": "form-control",
                                                              "placeholder": "Екатеринбург" }))