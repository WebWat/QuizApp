from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
import datetime
import uuid
from .models import (
    Test,
    Question, 
    SingleChoice, 
    SingleChoiceAnswers, 
    MultipleChoice, 
    MultipleChoiceAnswers,
    UserAnswers,
    QuestionResult,
    SingleChoiceResult,
    MultipleChoiceResult
)
from .forms import (
    TestForm, 
    QuestionForm, 
    AnswerForm, 
    EditQuestionForm
)

def index(request):
    data = { "tests": Test.objects.filter(is_published = True),
             "is_auth": request.user.is_authenticated,
             "username": request.user.username  }
    return render(request, "index.html", context = data)

def about(request, id):
    test = Test.objects.filter(id = id).first()
    if request.method == "POST":
        unique_id = uuid.uuid4().hex
        test.useranswers_set.create(id = unique_id)
        request.session["unique_id"] = unique_id
        return redirect(f"/test_run/{test.id}/0")
    data = { "test": test,
             "username": User.objects.filter(id = test.user_id).first().username }
    return render(request, "about.html", context = data)

def result(request, unique_id):
    try:
        user_answer = UserAnswers.objects.get(id = unique_id, is_finished = True)
        test = Test.objects.get(id = user_answer.test_id)
        questions = list()
        correct = 0
        results = QuestionResult.objects.filter(user_answers_id = unique_id)
        for result in results:
            question = Question.objects.get(id = result.question_id)
            answers = list()
            if question.choice_type == 0:
                if result.singlechoiceresult.chose == question.singlechoice.correct_answer:
                    correct += 1
                for answer in question.singlechoice.singlechoiceanswers_set.all():
                    answers.append((answer.text, 
                                    result.singlechoiceresult.chose == answer.id, 
                                    question.singlechoice.correct_answer == answer.id))
            else:
                question_answers = question.multiplechoice.multiplechoiceanswers_set.all()
                inc = question_answers.filter(is_correct = True).count() /  question_answers.count()
                current = 0
                for answer in question_answers:
                    chose_answers = result.multiplechoiceresult.multiplechoiceanswersresult_set.filter(chose = answer.id).count()
                    if chose_answers > 0 and answer.is_correct:
                        current += inc
                    elif chose_answers > 0 or answer.is_correct:
                        current -= inc
                    answers.append((answer.text, chose_answers > 0, answer.is_correct))
                current = 0 if current < 0 else current
                correct += current
            questions.append((question.issue, answers, question.choice_type))
        data = { "title": test.title,
                 "user_answers": user_answer, 
                 "questions": questions,
                 "correct": correct / len(questions) * 100 }
        return render(request, "result.html", context = data)
    except UserAnswers.DoesNotExist:
        return HttpResponseNotFound("<h2>Результат не найден</h2>")

def test_run(request, test_id, current):
    try:
        test = Test.objects.get(id = test_id)
        question = test.question_set.all()[current]
        if request.method == "POST":
            unique_id = request.session["unique_id"]
            answers = UserAnswers.objects.get(id = unique_id)
            _list = request.POST.getlist("answers")
            if len(_list) != 0:
                question_result = answers.questionresult_set.create(question_id = question.id)
                if question.choice_type == 0:
                    id = int(_list[0])
                    question_result.singlechoiceresult = SingleChoiceResult.objects.create(chose = id, question_id = question_result.id)
                else:
                    multiple_choice = MultipleChoiceResult.objects.create(question_id = question_result.id)
                    for id in _list:
                        multiple_choice.multiplechoiceanswersresult_set.create(chose = int(id))
                    question_result.multiplechoiceresult = multiple_choice
                question_result.save()
                if test.question_set.count() == current + 1:
                    answers.is_finished = True
                    answers.save()
                    return redirect(f"/result/{unique_id}")
                return redirect(f"/test_run/{test.id}/{current + 1}")
        answers = {}
        if question.choice_type == 0:
            for answer in question.singlechoice.singlechoiceanswers_set.all():
                answers[answer.id] = answer.text
        else:
            for answer in question.multiplechoice.multiplechoiceanswers_set.all():
                answers[answer.id] = answer.text
        data = { "question": question, "answers": answers }
        return render(request, "test_run.html", context = data)
    except (Test.DoesNotExist, UserAnswers.DoesNotExist):
        return HttpResponseNotFound("<h2>Тест не найден</h2>")

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
        questions = test.question_set.all()
        correct = True
        for question in questions:
            if question.choice_type == 0:
                answers = question.singlechoice.singlechoiceanswers_set.all()
                if answers.filter(id = question.singlechoice.correct_answer).count() == 0:
                    correct = False
                    break
            else:
                answers = MultipleChoiceAnswers.objects.filter(multiple_choice_id = question.id, is_correct = True)
                if answers.count() == 0:
                    correct = False
                    break
        if correct:
            test.is_published = True
            test.save()
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
                test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
                question = test.question_set.create(issue = form.cleaned_data["issue"], 
                                                    choice_type = int(form.cleaned_data["choice_type"]))
                if question.choice_type == 0:
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
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
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
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = Question.objects.get(test_id = test.id, id = id)
        question.delete()
        return redirect(f"/questions/{test_id}/")
    except (Test.DoesNotExist, Question.DoesNotExist):
        return HttpResponseNotFound("<h2>Вопрос не найден</h2>")

@login_required       
def set_true(request, test_id, question_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
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
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
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
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
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
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
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

