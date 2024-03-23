from django.contrib.auth.decorators import login_required
from django.contrib import auth 
from django.shortcuts import redirect, render
from .forms import (
    CustomLoginForm,
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
                return redirect("/profile")
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
def logout(request):
    auth.logout(request)
    return redirect("/")


