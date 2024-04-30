from django.contrib.auth.models import User
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from Main.settings import MEDIA_ROOT
from .helpers import get_average_all, get_average_for_single, get_average_for_multiple
import os
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
    MultipleChoiceResult,
    Tags
)
from .forms import (
    TestForm, 
    QuestionForm, 
    AnswerForm, 
    EditQuestionForm
)

# TODO: проблема c "Русский язык"
def index(request):
    title = "" if request.GET.get("title") == None else request.GET.get("title")
    initial = title
    orderBy = request.GET.get("orderBy")

    query = Test.objects.filter(is_published = True)
    if orderBy == "pass_rate":
        query = query.order_by("-" + orderBy)
    elif orderBy == "published_at":
        query = query.order_by(orderBy)
    
    tests = list(query)
    title = title.lower()

    # Проверяем теги
    if "!" in title:
        copy = tests.copy()
        tags = Tags.objects.all()
        for tag in tags:
            name = ("!" + tag.label).lower()
            if name in title:
                title = title.replace(name, "")
                for test in copy:
                    if not test.tags.contains(tag) and test in tests:
                        tests.remove(test)
    
    title = title.rstrip()
    # Ищем тесты по названию
    tests = list(filter(lambda test: title in test.title.lower(), tests))
    context = { "tests": tests,
                "title": initial,
                "selected": 0 if orderBy == "pass_rate" else 1,
                "username": request.user.username  }
    return render(request, "index.html", context)

def user_tests(request, username):
    try:
        user = User.objects.get(username = username)
        context = { "username": user.username, 
                    "tests": user.test_set.filter(is_published = True) }
        return render(request, "user_tests.html", context)
    except User.DoesNotExist:
        return redirect("/error")

def about(request, id):
    try:
        test = Test.objects.get(id = id)
        if request.method == "POST":
            # Создаем уникальный идентификатор теста
            unique_id = uuid.uuid4().hex
            request.session["unique_id"] = unique_id
            # Если пользователь авторизован, то привязываем тест
            if request.user.is_authenticated:
                test.useranswers_set.create(id = unique_id, user_id = request.user.id)
            else:
                test.useranswers_set.create(id = unique_id)
            return redirect(f"/test_run/{test.id}/")
        context = { "test": test,
                    "username": request.user.username,
                    "questions_count": test.question_set.all().count(),
                    "author": User.objects.get(id = test.user_id).username }
        return render(request, "about.html", context)
    except Test.DoesNotExist:
        return redirect("/error")

#@cache_page(30 * 60)
def result(request, unique_id):
    try:
        user_answer = UserAnswers.objects.get(id = unique_id, is_finished = True)
        test = Test.objects.get(id = user_answer.test_id)
        results = QuestionResult.objects.filter(user_answers_id = unique_id)
        total_user_answers = UserAnswers.objects.filter(test_id = test.id, is_finished = True)
        current_question = 0
        questions = list()
        
        # Заполняем questions list
        for result in results:
            question = Question.objects.get(id = result.question_id)
            answers = list()
            if question.choice_type == 0:
                for answer in question.singlechoice.singlechoiceanswers_set.all():
                    answers.append((answer.text, 
                                    result.singlechoiceresult.chose == answer.id, 
                                    question.singlechoice.correct_answer == answer.id,
                                    get_average_for_single(total_user_answers, current_question, answer.id)))
            else:
                question_answers = question.multiplechoice.multiplechoiceanswers_set.all()
                for answer in question_answers:
                    chose_answers = result.multiplechoiceresult.multiplechoiceanswersresult_set.filter(chose = answer.id).exists()
                    answers.append((answer.text, 
                                    chose_answers, 
                                    answer.is_correct, 
                                    get_average_for_multiple(total_user_answers, current_question, answer.id)))
            questions.append((question.issue, question.image, answers, question.choice_type))
            current_question += 1

        correct_rate_all = get_average_all(total_user_answers)

        context = { "title": test.title,
                    "id": user_answer.id,
                    "finished_at": user_answer.finished_at, 
                    "count": total_user_answers.count(),
                    "questions": questions,
                    "correct_rate_all": correct_rate_all,
                    "correct": user_answer.correct_answer_rate,
                    "username": request.user.username }
        return render(request, "result.html", context)
    except UserAnswers.DoesNotExist:
        return redirect("/error")

def test_run(request, test_id, unique_id = ""):
    try:
        test = Test.objects.get(id = test_id)
        # Если не в режиме "продолжения", то задаем новый идентификатор
        if unique_id == "":
            unique_id = request.session["unique_id"]
        user_answer = UserAnswers.objects.get(id = unique_id)
        questions = test.question_set.all()
        # Получаем текущий вопрос
        question = questions[user_answer.stage]

        if request.method == "POST":
            # Получаем список выбранных ответов
            _list = request.POST.getlist(f"answers-{question.id}")
            # Если имеется пользовательский ввод
            if len(_list) != 0:
                # Создаем результат
                question_result = user_answer.questionresult_set.create(question_id = question.id)
                # Если вопрос с одиночным выбором
                if question.choice_type == 0:
                    id = int(_list[0])
                    question_result.singlechoiceresult = SingleChoiceResult.objects.create(chose = id, 
                                                                                           question_result_id = question_result.id)
                    # Подсчитываем количество правильных ответов
                    if id == question.singlechoice.correct_answer:
                        user_answer.correct_answers += 1
                # Если вопрос с множественным выбором
                else:
                    # Создаем результат
                    multiple_choice = MultipleChoiceResult.objects.create(question_result_id = question_result.id)
                    for id in _list:
                        multiple_choice.multiplechoiceanswersresult_set.create(chose = int(id))
                    question_result.multiplechoiceresult = multiple_choice

                    # Получаем ответы
                    question_answers = question.multiplechoice.multiplechoiceanswers_set.all()
                    # Количество баллов за верный ответ
                    inc = 1 / question_answers.filter(is_correct = True).count()
                    # Подсчитываем количество правильных ответов
                    current = 0
                    for answer in question_answers:
                        # Выбран ли данный ответ пользователем?
                        answer_selected = question_result.multiplechoiceresult.multiplechoiceanswersresult_set.filter(chose = answer.id).exists()
                        if answer_selected and answer.is_correct:
                            current += inc
                        elif answer_selected:
                            current -= inc
                    current = 0 if current < 0 else current
                    user_answer.correct_answers += current

                # Сохраняем результат и идем к следующему вопросу
                question_result.save()
                user_answer.stage += 1
                user_answer.save()

                # Если вопрос последний, то переходим на страницу результата
                if test.question_set.count() == user_answer.stage:
                    user_answer.correct_answer_rate = user_answer.correct_answers / len(questions) * 100
                    user_answer.is_finished = True
                    user_answer.finished_at = datetime.datetime.now()
                    user_answer.save()

                    test.pass_rate += 1
                    test.save()
                    return redirect(f"/result/{unique_id}/")
                else:
                    question = questions[user_answer.stage]

        user_answers_dict = { }
        if question.choice_type == 0:
            for answer in question.singlechoice.singlechoiceanswers_set.all():
                user_answers_dict[answer.id] = answer.text
        else:
            for answer in question.multiplechoice.multiplechoiceanswers_set.all():
                user_answers_dict[answer.id] = answer.text

        context = { "question": question, 
                    "answers": user_answers_dict,
                    "total_questions": test.question_set.count(),
                    "current": user_answer.stage + 1,
                    "username": request.user.username }
        return render(request, "test_run.html", context)
    except (Test.DoesNotExist, UserAnswers.DoesNotExist):
        return redirect("/error")

@login_required 
def add_tag(request, test_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        total_tags = Tags.objects.all()

        if request.method == "POST":
            total = request.POST.getlist("tags")
            test.tags.clear()
            for id in total:
                test.tags.add(Tags.objects.get(id = id))
            test.save()

        test_tags = test.tags.all()
        tags_list = list()

        # Отмечаем существующие теги
        for tag in total_tags:
            if test_tags.contains(tag):
                tags_list.append((tag.label, tag.id, 1))
            else:
                tags_list.append((tag.label, tag.id, 0))

        context = { "test": test,
                    "tags": tags_list, 
                    "test_id": test_id,
                    "username": request.user.username }
        return render(request, "add_tag.html", context)
    except Test.DoesNotExist:
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
        return redirect(f"/questions/{test_id}/")
    except (Test.DoesNotExist, 
            Question.DoesNotExist, 
            SingleChoiceAnswers.DoesNotExist,
            MultipleChoiceAnswers.DoesNotExist):
        return redirect("/error")

@login_required
def history(request):
    user_answers = UserAnswers.objects.filter(user_id = request.user.id).order_by("test_id")
    results = list()
    _list = list()
    # Собственная реализация группировки
    if user_answers.count() > 0:
        test_id = user_answers[0].test_id
        for answer in user_answers:
            if answer.test_id != test_id:
                results.append((Test.objects.get(id = test_id).title, _list))
                test_id = answer.test_id
                _list = list()
            _list.append(answer)
        results.append((Test.objects.get(id = test_id).title, _list))

    context = { "user_answers": results,
                "username": request.user.username }
    return render(request, "history.html", context)

@login_required
def profile(request):
    context = { "tests": Test.objects.filter(user_id = request.user.id),
                "username": request.user.username }
    return render(request, "profile.html", context)

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
    context = { "username": request.user.username,
                "form": form }
    return render(request, "create_test.html", context)

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
                return redirect(f"/profile#item-{id}")
        else:
            form = TestForm(initial = { "title": test.title, "description": test.description })
        context = { "username": request.user.username,
                    "test_id": id,
                    "form": form }
        return render(request, "edit_test.html", context)
    except Test.DoesNotExist:
        return redirect("/error")

@login_required    
def delete_test(request, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = id)
        test.delete()
        return redirect("/profile")
    except Test.DoesNotExist:
        return redirect("/error")
    
#TODO: довести до ума
@login_required    
def publish_test(request, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = id)
        questions = test.question_set.all()
        correct = True
        for question in questions:
            # Если вопрос с одиночным выбором
            if question.choice_type == 0:
                answers = question.singlechoice.singlechoiceanswers_set.all()
                # Если не найдено ни одного верного ответа, то отклоняем
                if answers.filter(id = question.singlechoice.correct_answer).count() == 0:
                    correct = False
                    break
            # Если вопрос с множественным выбором
            else:
                answers = MultipleChoiceAnswers.objects.filter(multiple_choice_id = question.id, is_correct = True)
                # Если не найдено ни одного верного ответа, то отклоняем
                if answers.count() == 0:
                    correct = False
                    break
        if correct:
            test.is_published = True
            test.published_at = datetime.date.today()
            test.save()
        return redirect("/profile")
    except Test.DoesNotExist:
        return redirect("/error")
    
@login_required       
def questions(request, test_id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id)
        context = { "test": test, 
                    "questions": Question.objects.filter(test_id = test.id),
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
            form = EditQuestionForm(request.POST)
            if form.is_valid():
                question.issue = form.cleaned_data["issue"]
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
def delete_question(request, test_id, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = test_id, is_published = False)
        question = Question.objects.get(test_id = test.id, id = id)
        question.delete()
        # Если нашли изображение, то удаляем его
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

def error(request):
    return render(request, "error.html")