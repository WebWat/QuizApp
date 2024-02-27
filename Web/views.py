from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.shortcuts import (
    redirect,
    render,
)
from .forms import (
    CustomLoginForm,
    RegisterForm,
)

def index(request):
    return render(request, "index.html")

@login_required
def profile(request):
    data = {"username": request.user.username}
    return render(request, "profile.html", context=data)

def _login(request):
    if request.method == "POST":
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username = form.cleaned_data["username"], password = form.cleaned_data["password"])
            if user:
                login(request, user)
                return redirect("/profile")
    else:
        form = CustomLoginForm()
    return render(request, "login.html", {"form": form})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            user = form.save(commit = False)
            user.save(True)
            return redirect("/login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form })

@login_required
def _logout(request):
    logout(request)
    return redirect("/")
