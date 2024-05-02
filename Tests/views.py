from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
import datetime
from Web.models import (
    Test,
    Tags
)
from .forms import (
    TestForm
)

def user_tests(request, username):
    try:
        user = User.objects.get(username = username)
        context = { "username": request.user.username, 
                    "author": user.username,
                    "tests": user.test_set.filter(is_published = True) }
        return render(request, "user_tests.html", context)
    except User.DoesNotExist:
        return redirect("/error")
    
@login_required
def profile(request):
    context = { "tests": Test.objects.filter(user_id = request.user.id).order_by("-id"),
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
        messages.info(request, f"Тест \"{test.title}\" удален")
        return redirect("/profile")
    except Test.DoesNotExist:
        return redirect("/error")
    
@login_required    
def publish_test(request, id):
    try:
        test = Test.objects.get(user_id = request.user.id, id = id)
        questions = test.question_set.all()
        correct = True
        if questions.count() > 0:
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
                    answers = question.multiplechoice.multiplechoiceanswers_set.filter(is_correct = True)
                    # Если не найдено ни одного верного ответа, то отклоняем
                    if answers.count() == 0:
                        correct = False
                        break
            if correct:
                test.is_published = True
                test.published_at = datetime.date.today()
                test.save()
                messages.info(request, f"Тест \"{test.title}\" опубликован")
            else:
                messages.warning(request, f"Не удалось опубликовать тест \"{test.title}\", т.к. присутствует вопрос без правильного ответа")
        else:
            messages.warning(request, f"Не удалось опубликовать тест \"{test.title}\", т.к. отсутствуют вопросы")
        return redirect("/profile")
    except Test.DoesNotExist:
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
                test.tags.add(total_tags.get(id = id))
            test.save()
            messages.info(request, "Теги обновлены")

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
                    "username": request.user.username }
        return render(request, "add_tag.html", context)
    except Test.DoesNotExist:
        return redirect("/error")
