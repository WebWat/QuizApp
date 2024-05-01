from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.shortcuts import redirect, render
from .helpers import get_average_all, get_average_for_single, get_average_for_multiple
import datetime, uuid
from .models import (
    Test,
    UserAnswers,
    SingleChoiceResult,
    MultipleChoiceResult,
    Tags
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

#@cache_page(2 * 60)
def result(request, unique_id):
    try:
        user_answer = UserAnswers.objects.get(id = unique_id, is_finished = True)
        test = Test.objects.get(id = user_answer.test_id)
        init_questions = test.question_set.all()
        results = user_answer.questionresult_set.all()
        total_user_answers = UserAnswers.objects.filter(test_id = test.id, is_finished = True)
        total_user_answers_count = total_user_answers.count()
        current_question = 0
        questions = list()
        
        # Заполняем questions list
        for result in results:
            question = init_questions[current_question]
            answers = list()
            if question.choice_type == 0:
                question_answers = question.singlechoice.singlechoiceanswers_set.all()
                for answer in question_answers:
                    answers.append((answer.text, 
                                    result.singlechoiceresult.chose == answer.id, 
                                    question.singlechoice.correct_answer == answer.id,
                                    get_average_for_single(total_user_answers_count, question, answer.id)))
            else:
                question_answers = question.multiplechoice.multiplechoiceanswers_set.all()
                for answer in question_answers:
                    chose_answer = result.multiplechoiceresult.multiplechoiceanswersresult_set.filter(chose = answer.id).exists()
                    answers.append((answer.text, 
                                    chose_answer, 
                                    answer.is_correct, 
                                    get_average_for_multiple(question, answer.id)))
            questions.append((question.issue, question.image, answers, question.choice_type))
            current_question += 1

        correct_rate_all = get_average_all(total_user_answers)

        context = { "title": test.title,
                    "id": user_answer.id,
                    "finished_at": user_answer.finished_at, 
                    "count": total_user_answers_count,
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

        # Если вернулись к тесту после прохождения, то кидаем ошибку
        if questions.count() == user_answer.stage:
            return redirect("/error")
        
        # Получаем текущий вопрос
        question = questions[user_answer.stage]

        if request.method == "POST":
            # Получаем список выбранных ответов
            _list = request.POST.getlist(f"answers-{question.id}")
            # Если имеется пользовательский ввод
            if len(_list) != 0:
                # Создаем результат
                question_result = user_answer.questionresult_set.create()
                # Если вопрос с одиночным выбором
                if question.choice_type == 0:
                    id = int(_list[0])
                    question_result.singlechoiceresult = SingleChoiceResult.objects.create(chose = id, 
                                                                                           question_result_id = question_result.id)
                    # Подсчитываем количество правильных ответов
                    if id == question.singlechoice.correct_answer:
                        user_answer.correct_answers += 1

                    single = question.singlechoice.singlechoiceanswers_set.get(id = id)
                    single.count += 1
                    single.save()
                # Если вопрос с множественным выбором
                else:
                    # Создаем результат
                    multiple_choice_result = MultipleChoiceResult.objects.create(question_result_id = question_result.id)
                    question_answers = question.multiplechoice.multiplechoiceanswers_set.all()
                    total = 0
                    for id in _list:
                        int_id = int(id)
                        ans = question_answers.get(id = int_id)
                        ans.count += 1
                        ans.save()
                        total += 1
                        multiple_choice_result.multiplechoiceanswersresult_set.create(chose = int_id)
                    question_result.multiplechoiceresult = multiple_choice_result

                    # Получаем ответы
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

                    question.multiplechoice.total_count += total
                    question.multiplechoice.save()

                # Сохраняем результат и идем к следующему вопросу
                question_result.save()
                user_answer.stage += 1
                user_answer.save()

                # Если вопрос последний, то переходим на страницу результата
                if questions.count() == user_answer.stage:
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
    
def error(request):
    return render(request, "error.html")