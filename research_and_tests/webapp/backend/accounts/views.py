from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            print("User registered:", user.username)  # Debug: Print username to confirm registration
            return redirect('home')  # Redirect to the home page after registration
        else:
            print("Form errors:", form.errors)  # Debug: Print form errors if validation fails
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})
