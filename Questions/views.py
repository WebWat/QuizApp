from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from Main.settings import MEDIA_ROOT
import os, uuid
from Web.helpers import get_average_for_single, get_average_for_multiple, get_average_all
from Web.models import (
    Test,
    Question, 
    SingleChoice, 
    SingleChoiceAnswers, 
    MultipleChoice, 
    MultipleChoiceAnswers,
    UserAnswers,
)
from .forms import (
    QuestionForm, 
    AnswerForm, 
    EditQuestionForm
)

@login_required       
def questions(request, test_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        questions_stats = list()
        correct_rate_all = 0

        if test.is_published:
            questions = test.question_set.all()
            total_user_answers = UserAnswers.objects.filter(test_id = test.id, is_finished = True)
            correct_rate_all = get_average_all(total_user_answers)
            current_question = 0

            # Заполняем questions stats
            for question in questions:
                answers = list()
                if question.choice_type == 0:
                    for answer in question.singlechoice.singlechoiceanswers_set.all():
                        answers.append((answer.text, 
                                        question.singlechoice.correct_answer == answer.id,
                                        get_average_for_single(total_user_answers, current_question, answer.id)))
                else:
                    question_answers = question.multiplechoice.multiplechoiceanswers_set.all()
                    for answer in question_answers:
                        answers.append((answer.text, 
                                        answer.is_correct, 
                                        get_average_for_multiple(total_user_answers, current_question, answer.id)))
                questions_stats.append((question.issue, question.image, answers, question.choice_type))
                current_question += 1
                
        context = { "test": test, 
                    "questions_stats": questions_stats,
                    "correct_rate_all": correct_rate_all,
                    "questions": test.question_set.all(),
                    "username": request.user.username }
        return render(request, "questions.html", context)
    except Test.DoesNotExist:
        return redirect("/error")

@login_required
def create_question(request, test_id):
    try:
        if request.method == "POST":
            form = QuestionForm(request.POST, request.FILES)
            if form.is_valid():
                test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
                image = form.cleaned_data["image"]
                if image:
                    if image.content_type == "image/png":
                        image.name = str(uuid.uuid4()) + ".png"
                    elif image.content_type == "image/jpeg":
                        image.name = str(uuid.uuid4()) + ".jpg"
                    else:
                        messages.warning(request, "Рисунки поддерживаются только в формате png или jpeg")
                        image = None
                question = test.question_set.create(issue = form.cleaned_data["issue"], 
                                                    choice_type = int(form.cleaned_data["choice_type"]),
                                                    image = image)
                # Если вопрос с одиночным выбором
                if question.choice_type == 0:
                    SingleChoice.objects.create(question = question)
                # Если вопрос с множественным выбором
                else:
                    MultipleChoice.objects.create(question = question)
                return redirect(f"/questions/{test_id}/")
        else:
            form = QuestionForm()
        context = { "username": request.user.username,
                    "test_id": test_id,
                    "form": form }
        return render(request, "create_question.html", context)
    except Test.DoesNotExist:
        return redirect("/error")

@login_required
def edit_question(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = Question.objects.get(test_id = test.id, id = id)
        if request.method == "POST":
            form = EditQuestionForm(request.POST, request.FILES)
            if form.is_valid():
                question.issue = form.cleaned_data["issue"]
                image = form.cleaned_data["image"]
                if image:
                    if image.content_type == "image/png":
                        image.name = str(uuid.uuid4()) + ".png"
                    elif image.content_type == "image/jpeg":
                        image.name = str(uuid.uuid4()) + ".jpg"
                    else:
                        messages.warning(request, "Рисунки поддерживаются только в формате png или jpeg")
                        image = None
                if image:
                    # Удаляем старый рисунок
                    if question.image:
                        path = os.path.join(MEDIA_ROOT, question.image.name)
                        if os.path.exists(path):
                            os.remove(path)

                    question.image = image
                question.save()
                return redirect(f"/questions/{test_id}#item-{id}")
        else:
            form = EditQuestionForm(initial = { "issue": question.issue })
        context = { "username": request.user.username,
                    "test_id": test_id,
                    "question_id": id,
                    "form": form }
        return render(request, "edit_question.html", context)
    except (Test.DoesNotExist, Question.DoesNotExist):
        return redirect("/error")
    
@login_required    
def delete_image(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = Question.objects.get(test_id = test.id, id = id)
        if question.image:
            path = os.path.join(MEDIA_ROOT, question.image.name)
            if os.path.exists(path):
                os.remove(path)
            question.image = None
            question.save()
        return redirect(f"/questions/{test_id}#item-{id}")
    except (Test.DoesNotExist, Question.DoesNotExist):
        return redirect("/error")
    
@login_required    
def delete_question(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = Question.objects.get(test_id = test.id, id = id)
        if question.image:
            path = os.path.join(MEDIA_ROOT, question.image.name)
            if os.path.exists(path):
                os.remove(path)
        return redirect(f"/questions/{test_id}/")
    except (Test.DoesNotExist, Question.DoesNotExist):
        return redirect("/error")

@login_required       
def set_true(request, test_id, question_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = Question.objects.get(test_id = test.id, id = question_id)
        # Если вопрос с одиночным выбором
        if question.choice_type == 0:
            choice = SingleChoice.objects.get(question_id = question.id)
            answers = SingleChoiceAnswers.objects.filter(single_choice_id = question.id)
            # Если нашли идентификатор ответа в списке, то указываем ответ как верный
            if answers.filter(id = id).count() > 0:
                choice.correct_answer = id
                choice.save()
        # Если вопрос с множественным выбором
        else:
            answer = MultipleChoiceAnswers.objects.get(id = id, multiple_choice_id = question.id)
            answer.is_correct = not answer.is_correct
            answer.save()
        return redirect(f"/questions/{test_id}#item-{question_id}")
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoice.DoesNotExist, 
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return redirect("/error")

@login_required
def create_answer(request, test_id, question_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = Question.objects.get(test_id = test.id, id = question_id)
        if request.method == "POST":
            form = AnswerForm(request.POST)
            if form.is_valid():
                # Если вопрос с одиночным выбором
                if question.choice_type == 0:
                    single_choice = SingleChoice.objects.get(question_id = question.id)
                    single_choice.singlechoiceanswers_set.create(text = form.cleaned_data["text"])
                # Если вопрос с множественным выбором
                else:
                    multiple_choice = MultipleChoice.objects.get(question_id = question.id)
                    multiple_choice.multiplechoiceanswers_set.create(text = form.cleaned_data["text"])
                return redirect(f"/questions/{test_id}#item-{question_id}")
        else:
            form = AnswerForm()
        context = { "username": request.user.username,
                    "question_id": question_id,
                    "test_id": test_id,
                    "form": form }
        return render(request, "create_answer.html", context)
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoice.DoesNotExist, 
            MultipleChoice.DoesNotExist):
        return redirect("/error")

@login_required
def edit_answer(request, test_id, question_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = Question.objects.get(test_id = test.id, id = question_id)
        # Если вопрос с одиночным выбором
        if question.choice_type == 0:
            answer = SingleChoiceAnswers.objects.get(single_choice_id = question_id, id = id)
        # Если вопрос с множественным выбором
        else:
            answer = MultipleChoiceAnswers.objects.get(multiple_choice_id = question_id, id = id)

        if request.method == "POST":
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer.text = form.cleaned_data["text"]
                answer.save()
                return redirect(f"/questions/{test_id}#item-{question_id}")
        else:
            form = AnswerForm(initial = { "text": answer.text })

        context = { "username": request.user.username,
                    "question_id": question_id,
                    "test_id": test_id,
                    "form": form }
        return render(request, "edit_answer.html", context)
    except (Test.DoesNotExist, 
            Question.DoesNotExist,
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return redirect("/error")

@login_required    
def delete_answer(request, test_id, question_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = Question.objects.get(test_id = test.id, id = question_id)
        # Если вопрос с одиночным выбором
        if question.choice_type == 0:
            answer = SingleChoiceAnswers.objects.get(single_choice_id = question_id, id = id)
        # Если вопрос с множественным выбором
        else:
            answer = MultipleChoiceAnswers.objects.get(multiple_choice_id = question_id, id = id)
        answer.delete()
        return redirect(f"/questions/{test_id}#item-{question_id}")
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return redirect("/error")
    