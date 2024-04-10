from django.contrib.auth.models import User
from django.db import models

class Test(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 200)
    description = models.CharField(max_length = 2000)
    is_published = models.BooleanField(default = False)
    created_at = models.DateField()

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete = models.CASCADE)
    issue = models.CharField(max_length = 1000)
    choice_type = models.IntegerField(default = 0)
    #explanation = models.CharField(max_length = 2000, default = "")

class SingleChoice(models.Model):
    question = models.OneToOneField(Question, on_delete = models.CASCADE, primary_key = True)
    correct_answer = models.IntegerField(default = 0)

class SingleChoiceAnswers(models.Model):
    single_choice = models.ForeignKey(SingleChoice, on_delete = models.CASCADE)
    text = models.CharField(max_length = 100)
    
class MultipleChoice(models.Model):
    question = models.OneToOneField(Question, on_delete = models.CASCADE, primary_key = True)

class MultipleChoiceAnswers(models.Model):
    multiple_choice = models.ForeignKey(MultipleChoice, on_delete = models.CASCADE)
    text = models.CharField(max_length = 100)
    is_correct = models.BooleanField(default = False)

class UserAnswers(models.Model):
    id = models.CharField(max_length = 32, primary_key = True)
    test = models.ForeignKey(Test, on_delete = models.CASCADE)
    stage = models.IntegerField(default = 0)
    user_id = models.IntegerField(default = -1)
    correct_answer_rate = models.FloatField(default = -1)
    is_finished = models.BooleanField(default = False)

class QuestionResult(models.Model):
    user_answers = models.ForeignKey(UserAnswers, on_delete = models.CASCADE)
    question_id = models.IntegerField(default = -1)

class SingleChoiceResult(models.Model):
    question_result = models.OneToOneField(QuestionResult, on_delete = models.CASCADE, primary_key = True)
    chose = models.IntegerField()

class MultipleChoiceResult(models.Model):
    question_result = models.OneToOneField(QuestionResult, on_delete = models.CASCADE, primary_key = True)

class MultipleChoiceAnswersResult(models.Model):
    multiple_choice_result = models.ForeignKey(MultipleChoiceResult, on_delete = models.CASCADE)
    chose = models.IntegerField(default = -1)
    
    
