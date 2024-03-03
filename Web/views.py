import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Test
from django.contrib import auth 
from django.http import HttpResponseNotFound
from django.shortcuts import (
    redirect,
    render,
)
from .forms import (
    CustomLoginForm,
    RegisterForm,
    TestForm
)

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
        test = Test.objects.get(user_id = request.user, id = id)
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
        return HttpResponseNotFound("<h2>Test not found</h2>")

@login_required    
def delete_test(request, id):
    try:
        test = Test.objects.get(user_id = request.user, id = id)
        test.delete()
        return redirect("/profile")
    except Test.DoesNotExist:
        return HttpResponseNotFound("<h2>Test not found</h2>")

def login(request):
    if request.method == "POST":
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username = form.cleaned_data["username"], password = form.cleaned_data["password"])
            if user:
                auth.login(request, user)
                return redirect("/profile")
    else:
        form = CustomLoginForm()
    return render(request, "login.html", { "form": form })

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.save(True) # ?
            return redirect("/login")
    else:
        form = RegisterForm()
    return render(request, "register.html", { "form": form })

@login_required
def logout(request):
    auth.logout(request)
    return redirect("/")

