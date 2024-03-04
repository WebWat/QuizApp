from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
import datetime
from .models import Test, Question, SingleChoice, SingleChoiceAnswers, MultipleChoice, MultipleChoiceAnswers
from .forms import TestForm, QuestionForm, SingleAnswerForm, MultipleAnswerForm
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
                question = test.question_set.create(issue = form.cleaned_data["issue"], 
                                                    choice_type = form.cleaned_data["choice_type"])
                if question.choice_type == "0":
                    question.singlechoice_set.create()
                else:
                    question.multiplechoice_set.create()
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
            form = QuestionForm(request.POST)
            if form.is_valid():
                question.issue = form.cleaned_data["issue"]
                #TODO: добавить проверку ответов
                #question.choice_type = form.cleaned_data["choice_type"]
                question.save()
                return redirect(f"/questions/{test_id}/")
        else:
            form = QuestionForm(initial = { "issue": question.issue, "choice_type": question.choice_type })
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
def answers(request, test_id, question_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = question_id)
        if question.choice_type == 0:
            single_choice = SingleChoice.objects.get(question_id = question.id)
            answers = SingleChoiceAnswers.objects.filter(single_choice_id = single_choice.id)
            if request.method == "POST":
                correct_id = request.POST.get("correct_id")
                if answers.filter(id = correct_id).count() > 0:
                    single_choice.correct_answer = correct_id
                    single_choice.save()
            data = { "test": test, 
                     "question": question,
                     "correct_answer": single_choice.correct_answer, 
                     "answers": answers }
        else:
            multiple_choice = MultipleChoice.objects.get(question_id = question.id)
            data = { "test": test, 
                     "question": question,
                     "answers": MultipleChoiceAnswers.objects.filter(multiple_choice_id = multiple_choice.id) }
        return render(request, "answers.html", context = data)
    except (Test.DoesNotExist, Question.DoesNotExist, SingleChoice.DoesNotExist, MultipleChoice.DoesNotExist):
        return HttpResponseNotFound("<h2>Вопрос не найден</h2>")

#TODO: Разделить маршрутизацию для разных типов вопроса???  
@login_required
def create_answer(request, test_id, question_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = question_id)
        if request.method == "POST":
            if question.choice_type == 0:
                form = SingleAnswerForm(request.POST)
            else:
                form = MultipleAnswerForm(request.POST)
            if form.is_valid():
                if question.choice_type == 0:
                    single_choice = SingleChoice.objects.get(question_id = question.id)
                    single_choice.singlechoiceanswers_set.create(text = form.cleaned_data["text"])
                else:
                    multiple_choice = MultipleChoice.objects.get(question_id = question.id)
                    multiple_choice.multiplechoiceanswers_set.create(text = form.cleaned_data["text"],
                                                                     is_correct = form.cleaned_data["is_correct"])
                return redirect(f"/answers/{test_id}/{question_id}/")
        else:
            if question.choice_type == 0:
                form = SingleAnswerForm()
            else:
                form = MultipleAnswerForm()
        return render(request, "create_answer.html", { "form": form })
    except (Test.DoesNotExist, Question.DoesNotExist, SingleChoice.DoesNotExist, MultipleChoice.DoesNotExist):
        return HttpResponseNotFound("<h2>Ответ не найден</h2>")

@login_required
def edit_answer(request, test_id, question_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = question_id)
        if question.choice_type == 0:
            choice = SingleChoice.objects.get(question_id = question.id)
            answer = SingleChoiceAnswers.objects.get(single_choice_id = choice.id, id = id)
        else:
            choice = MultipleChoice.objects.get(question_id = question.id)
            answer = MultipleChoiceAnswers.objects.get(multiple_choice_id = choice.id, id = id)
        if request.method == "POST":
            if question.choice_type == 0:
                form = SingleAnswerForm(request.POST)
            else:
                form = MultipleAnswerForm(request.POST)
            if form.is_valid():
                answer.text = form.cleaned_data["text"]
                if question.choice_type == 1:
                    answer.is_correct = form.cleaned_data["is_correct"]
                answer.save()
                return redirect(f"/answers/{test_id}/{question_id}/")
        else:
            if question.choice_type == 0:
                form = SingleAnswerForm(initial = { "text": answer.text })
            else:
                form = MultipleAnswerForm(initial = { "text": answer.text, "is_correct": int(answer.is_correct) })
        return render(request, "edit_answer.html", { "form": form })
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoice.DoesNotExist, 
            MultipleChoice.DoesNotExist,
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return HttpResponseNotFound("<h2>Ответ не найден</h2>")

@login_required    
def delete_answer(request, test_id, question_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        question = Question.objects.get(test_id = test.id, id = question_id)
        if question.choice_type == 0:
            choice = SingleChoice.objects.get(question_id = question.id)
            answer = SingleChoiceAnswers.objects.get(single_choice_id = choice.id, id = id)
        else:
            choice = MultipleChoice.objects.get(question_id = question.id)
            answer = MultipleChoiceAnswers.objects.get(multiple_choice_id = choice.id, id = id)
        answer.delete()
        return redirect(f"/answers/{test_id}/{question_id}/")
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoice.DoesNotExist, 
            MultipleChoice.DoesNotExist,
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return HttpResponseNotFound("<h2>Ответ не найден</h2>")
