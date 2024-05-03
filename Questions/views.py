from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
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
        questions = test.question_set.all()
        questions_list = list()
        correct_rate_all = 0

        if test.is_published:
            total_user_answers = test.useranswers_set.filter(is_finished = True)
            correct_rate_all = get_average_all(total_user_answers)

            # Заполняем questions_list
            for question in questions:
                answers = list()
                # Если вопрос с одиночным ответом
                if question.choice_type == 0:
                    for answer in question.singlechoice.singlechoiceanswers_set.all():
                        answers.append((answer.text, 
                                        question.singlechoice.correct_answer == answer.id,
                                        get_average_for_single(total_user_answers.count(), question, answer.id)))
                # Если вопрос с множественным ответом
                else:
                    question_answers = question.multiplechoice.multiplechoiceanswers_set.all()
                    for answer in question_answers:
                        answers.append((answer.text, 
                                        answer.is_correct, 
                                        get_average_for_multiple(question, answer.id)))
                questions_list.append((question.issue, question.image, answers, question.choice_type))
                
        context = { "test": test, 
                    "questions_list": questions_list,
                    "correct_rate_all": correct_rate_all,
                    "questions": questions,
                    "username": request.user.username }
        
        return render(request, "Questions/questions.html", context)
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
        return render(request, "Questions/create_question.html", context)
    except Test.DoesNotExist:
        return redirect("/error")

@login_required
def edit_question(request, test_id, question_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = test.question_set.get(id = question_id)
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
                return redirect(f"/questions/{test_id}#item-{question_id}")
        else:
            form = EditQuestionForm(initial = { "issue": question.issue })
        context = { "username": request.user.username,
                    "test_id": test_id,
                    "question_id": question_id,
                    "form": form }
        return render(request, "Questions/edit_question.html", context)
    except (Test.DoesNotExist, Question.DoesNotExist):
        return redirect("/error")
    
@login_required    
def delete_image(request, test_id, question_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = test.question_set.get(id = question_id)
        if question.image:
            path = os.path.join(MEDIA_ROOT, question.image.name)
            if os.path.exists(path):
                os.remove(path)
            question.image = None
            question.save()
        return redirect(f"/questions/{test_id}#item-{question_id}")
    except (Test.DoesNotExist, Question.DoesNotExist):
        return redirect("/error")
    
@login_required    
def delete_question(request, test_id, question_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = test.question_set.get(id = question_id)
        if question.image:
            path = os.path.join(MEDIA_ROOT, question.image.name)
            if os.path.exists(path):
                os.remove(path)
        question.delete()
        return redirect(f"/questions/{test_id}/")
    except (Test.DoesNotExist, Question.DoesNotExist):
        return redirect("/error")

@login_required       
def set_true(request, test_id, question_id, answer_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = test.question_set.get(id = question_id)
        # Если вопрос с одиночным выбором
        if question.choice_type == 0:
            answers_count = question.singlechoice.singlechoiceanswers_set.filter(id = answer_id).count()
            # Если нашли идентификатор ответа в списке, то указываем ответ как верный
            if answers_count > 0:
                question.singlechoice.correct_answer = answer_id
                question.singlechoice.save()
        # Если вопрос с множественным выбором
        else:
            answer = question.multiplechoice.multiplechoiceanswers_set.get(id = answer_id)
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
        question = test.question_set.get(id = question_id)
        if request.method == "POST":
            form = AnswerForm(request.POST)
            if form.is_valid():
                # Если вопрос с одиночным выбором
                if question.choice_type == 0:
                    SingleChoiceAnswers.objects.create(text = form.cleaned_data["text"],
                                                       single_choice_id = question.id)
                # Если вопрос с множественным выбором
                else:
                    MultipleChoiceAnswers.objects.create(text = form.cleaned_data["text"],
                                                         multiple_choice_id = question.id)
                return redirect(f"/questions/{test_id}#item-{question_id}")
        else:
            form = AnswerForm()
        context = { "username": request.user.username,
                    "question_id": question_id,
                    "test_id": test_id,
                    "form": form }
        return render(request, "Questions/create_answer.html", context)
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoice.DoesNotExist, 
            MultipleChoice.DoesNotExist):
        return redirect("/error")

@login_required
def edit_answer(request, test_id, question_id, answer_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = test.question_set.get(id = question_id)
        # Если вопрос с одиночным выбором
        if question.choice_type == 0:
            answer = question.singlechoice.singlechoiceanswers_set.get(single_choice_id = question_id, 
                                                                       id = answer_id)
        # Если вопрос с множественным выбором
        else:
            answer = question.multiplechoice.multiplechoiceanswers_set.get(multiple_choice_id = question_id, 
                                                                           id = answer_id)

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
        return render(request, "Questions/edit_answer.html", context)
    except (Test.DoesNotExist, 
            Question.DoesNotExist,
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return redirect("/error")

@login_required    
def delete_answer(request, test_id, question_id, answer_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = test.question_set.get(test_id = test.id, id = question_id)
        # Если вопрос с одиночным выбором
        if question.choice_type == 0:
            answer = question.singlechoice.singlechoiceanswers_set.get(single_choice_id = question_id, 
                                                                       id = answer_id)
        # Если вопрос с множественным выбором
        else:
            answer = question.multiplechoice.multiplechoiceanswers_set.get(multiple_choice_id = question_id, 
                                                                           id = answer_id)
        answer.delete()
        return redirect(f"/questions/{test_id}#item-{question_id}")
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return redirect("/error")
    