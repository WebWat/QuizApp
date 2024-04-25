from django.contrib.auth.decorators import login_required
from django.contrib import auth 
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from .forms import (
    CustomLoginForm,
    CustomPasswordChangeForm,
    LoginChangeForm,
    RegisterForm
)

def login(request):
    if request.method == "POST":
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username = form.cleaned_data["username"],
                                     password = form.cleaned_data["password"])
            if user:
                auth.login(request, user)
                path = request.GET.get("next") if request.GET.get("next") else "/profile"
                return redirect(path)
    else:
        form = CustomLoginForm()
    return render(request, "login.html", { "form": form })

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.save(True)
            return redirect("/login")
    else:
        form = RegisterForm()
    return render(request, "register.html", { "form": form })

@login_required
def change_password(request):
    user = User.objects.get(username = request.user.username)
    if request.method == "POST":
        form = CustomPasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            auth.update_session_auth_hash(request, user)
            return redirect("/change_password")
    else:
        form = CustomPasswordChangeForm(user)
    context = { "username": request.user.username,
                "form": form }
    return render(request, "change_password.html", context)

@login_required
def change_login(request):
    if request.method == "POST":
        form = LoginChangeForm(request.POST)
        if form.is_valid() and User.objects.filter(username = form.cleaned_data["username"]).count() == 0:
            user = User.objects.get(username = request.user.username)
            user.username = form.cleaned_data["username"]
            user.save()
            return redirect("/change_login")
    else:
        form = LoginChangeForm()
    context = { "username": request.user.username,
                "form": form }
    return render(request, "change_login.html", context)

@login_required
def logout(request):
    auth.logout(request)
    return redirect("/")


