from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from users.forms import CustomUserCreationForm

def dashboard(request):
    return render(request, "dashboard.html")

    
def register(request):
    if request.method == "GET":
        return render(
            request, "register.html",
            {"form": CustomUserCreationForm }
        )
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # replace with this line
            user.backend = "django.contrib.auth.backends.ModelBackend" # replace with this line
            user.save() # and replace with this line
            login(request, user)
            return redirect(reverse("dashboard"))