from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
import datetime
from .models import (
    Test,
    Question, 
    SingleChoice, 
    SingleChoiceAnswers, 
    MultipleChoice, 
    MultipleChoiceAnswers
)
from .forms import (
    TestForm, 
    QuestionForm, 
    AnswerForm, 
    EditQuestionForm
)
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
def publish_test(request, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = id)
        test.is_published = True
        test.save()
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
                question = test.question_set.create(issue = form.cleaned_data["issue"], 
                                                    choice_type = form.cleaned_data["choice_type"])
                if question.choice_type == "0":
                    SingleChoice.objects.create(question = question)
                else:
                    MultipleChoice.objects.create(question = question)
                return redirect(f"/questions/{test_id}/")
        else:
            form = QuestionForm()
        return render(request, "create_question.html", { "form": form })
    except Test.DoesNotExist:
        return HttpResponseNotFound("<h2>Вопрос не найден</h2>")

@login_required
def edit_question(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = id)
        if request.method == "POST":
            form = EditQuestionForm(request.POST)
            if form.is_valid():
                question.issue = form.cleaned_data["issue"]
                question.save()
                return redirect(f"/questions/{test_id}/")
        else:
            form = EditQuestionForm(initial = { "issue": question.issue })
        return render(request, "edit_question.html", { "form": form })
    except (Test.DoesNotExist, Question.DoesNotExist):
        return HttpResponseNotFound("<h2>Вопрос не найден</h2>")

@login_required    
def delete_question(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = id)
        question.delete()
        return redirect(f"/questions/{test_id}/")
    except (Test.DoesNotExist, Question.DoesNotExist):
        return HttpResponseNotFound("<h2>Вопрос не найден</h2>")

@login_required       
def set_true(request, test_id, question_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = question_id)
        if question.choice_type == 0:
            choice = SingleChoice.objects.get(question_id = question.id)
            answers = SingleChoiceAnswers.objects.filter(single_choice_id = question.id)
            if answers.filter(id = id).count() > 0:
                choice.correct_answer = id
                choice.save()
        else:
            answer = MultipleChoiceAnswers.objects.get(id = id, multiple_choice_id = question.id)
            answer.is_correct = not answer.is_correct
            answer.save()
        return redirect(f"/questions/{test_id}/")
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoice.DoesNotExist, 
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return HttpResponseNotFound("<h2>Вопрос не найден</h2>")

@login_required
def create_answer(request, test_id, question_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = question_id)
        if request.method == "POST":
            form = AnswerForm(request.POST)
            if form.is_valid():
                if question.choice_type == 0:
                    single_choice = SingleChoice.objects.get(question_id = question.id)
                    single_choice.singlechoiceanswers_set.create(text = form.cleaned_data["text"])
                else:
                    multiple_choice = MultipleChoice.objects.get(question_id = question.id)
                    multiple_choice.multiplechoiceanswers_set.create(text = form.cleaned_data["text"])
                return redirect(f"/questions/{test_id}/")
        else:
            form = AnswerForm()
        return render(request, "create_answer.html", { "form": form })
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoice.DoesNotExist, 
            MultipleChoice.DoesNotExist):
        return HttpResponseNotFound("<h2>Ответ не найден</h2>")

@login_required
def edit_answer(request, test_id, question_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = question_id)
        if question.choice_type == 0:
            answer = SingleChoiceAnswers.objects.get(single_choice_id = question_id, id = id)
        else:
            answer = MultipleChoiceAnswers.objects.get(multiple_choice_id = question_id, id = id)
        if request.method == "POST":
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer.text = form.cleaned_data["text"]
                answer.save()
                return redirect(f"/questions/{test_id}/")
        else:
            form = AnswerForm(initial = { "text": answer.text })
        return render(request, "edit_answer.html", { "form": form })
    except (Test.DoesNotExist, 
            Question.DoesNotExist,
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return HttpResponseNotFound("<h2>Ответ не найден</h2>")

@login_required    
def delete_answer(request, test_id, question_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = question_id)
        if question.choice_type == 0:
            answer = SingleChoiceAnswers.objects.get(single_choice_id = question_id, id = id)
        else:
            answer = MultipleChoiceAnswers.objects.get(multiple_choice_id = question_id, id = id)
        answer.delete()
        return redirect(f"/questions/{test_id}/")
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return HttpResponseNotFound("<h2>Ответ не найден</h2>")

