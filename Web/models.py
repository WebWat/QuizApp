from django.contrib.auth.models import User
from django.db import models

class Test(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 200)
    description = models.CharField(max_length = 2000)
    pass_rate = models.IntegerField(default = 0)
    created_at = models.DateField()

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete = models.CASCADE)
    issue = models.CharField(max_length = 1000)
    explanation = models.CharField(max_length = 2000)
