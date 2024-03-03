from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
import datetime
from .models import Test, Question, SingleChoice, SingleChoiceAnswers, MultipleChoice, MultipleChoiceAnswers
from .forms import TestForm, QuestionForm
from django.shortcuts import redirect, render

def index(request):
    return render(request, "index.html")

@login_required
def profile(request):
    data = { "username": request.user.username, 
             "tests": Test.objects.filter(user_id = request.user.id) }
    return render(request, "profile.html", context = data)

@login_required
def create_test(request):
    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            request.user.test_set.create(title = form.cleaned_data["title"], 
                                        description = form.cleaned_data["description"],
                                        created_at = datetime.date.today())
            return redirect("/profile")
    else:
        form = TestForm()
    return render(request, "create_test.html", { "form": form })

@login_required
def edit_test(request, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = id)
        if request.method == "POST":
            form = TestForm(request.POST)
            if form.is_valid():
                test.title = form.cleaned_data["title"]
                test.description = form.cleaned_data["description"]
                test.save()
                return redirect("/profile")
        else:
            form = TestForm(initial = { "title": test.title, "description": test.description })
        return render(request, "edit_test.html", { "form": form })
    except Test.DoesNotExist:
        return HttpResponseNotFound("<h2>Тест не найден</h2>")

@login_required    
def delete_test(request, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = id)
        test.delete()
        return redirect("/profile")
    except Test.DoesNotExist:
        return HttpResponseNotFound("<h2>Тест не найден</h2>")
    
@login_required       
def questions(request, test_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        data = { "test": test, 
                 "questions": Question.objects.filter(test_id = test.id) }
        return render(request, "questions.html", context = data)
    except Test.DoesNotExist:
        return HttpResponseNotFound("<h2>Тест не найден</h2>")
    
@login_required
def create_question(request, test_id):
    try:
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                test = Test.objects.get(user_id = request.user.id, id = test_id)
                test.question_set.create(issue = form.cleaned_data["issue"], 
                                        choice_type = form.cleaned_data["choice_type"])
                return redirect(f"/questions/{test_id}/")
        else:
            form = QuestionForm()
        return render(request, "create_question.html", { "form": form })
    except Test.DoesNotExist:
        return HttpResponseNotFound("<h2>Тест не найден</h2>")

@login_required
def edit_question(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = id)
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                question.issue = form.cleaned_data["issue"]
                question.choice_type = form.cleaned_data["choice_type"] #TODO: добавить проверку ответов
                question.save()
                return redirect(f"/questions/{test_id}/")
        else:
            form = QuestionForm(initial = { "issue": question.issue, "choice_type": question.choice_type })
        return render(request, "edit_question.html", { "form": form })
    except (Test.DoesNotExist, Question.DoesNotExist):
        return HttpResponseNotFound("<h2>Сущность не найдена</h2>")

@login_required    
def delete_question(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = id)
        question.delete()
        return redirect(f"/questions/{test_id}/")
    except (Test.DoesNotExist, Question.DoesNotExist):
        return HttpResponseNotFound("<h2>Сущность не найдена</h2>")
    
@login_required       
def answers(request, test_id, question_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = question_id)
        data = { "test": test, 
                 "question": question,
                 "answers": Question.objects.filter(test_id = test.id) }
        return render(request, "questions.html", context = data)
    except (Test.DoesNotExist, Question.DoesNotExist):
        return HttpResponseNotFound("<h2>Сущность не найдена</h2>")
    
@login_required
def create_question(request, test_id):
    try:
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                test = Test.objects.get(user_id = request.user.id, id = test_id)
                test.question_set.create(issue = form.cleaned_data["issue"], 
                                        choice_type = form.cleaned_data["choice_type"])
                return redirect(f"/questions/{test_id}/")
        else:
            form = QuestionForm()
        return render(request, "create_question.html", { "form": form })
    except Test.DoesNotExist:
        return HttpResponseNotFound("<h2>Тест не найден</h2>")

@login_required
def edit_question(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = id)
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                question.issue = form.cleaned_data["issue"]
                question.choice_type = form.cleaned_data["choice_type"] #TODO: добавить проверку ответов
                question.save()
                return redirect(f"/questions/{test_id}/")
        else:
            form = QuestionForm(initial = { "issue": question.issue, "choice_type": question.choice_type })
        return render(request, "edit_question.html", { "form": form })
    except (Test.DoesNotExist, Question.DoesNotExist):
        return HttpResponseNotFound("<h2>Сущность не найдена</h2>")

@login_required    
def delete_question(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = id)
        question.delete()
        return redirect(f"/questions/{test_id}/")
    except (Test.DoesNotExist, Question.DoesNotExist):
        return HttpResponseNotFound("<h2>Сущность не найдена</h2>")
