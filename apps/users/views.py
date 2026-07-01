from django.shortcuts import render, redirect
from django.contrib.auth import login
from apps.dictionary.forms import CustomUserCreationForm # Форму можно оставить в dictionary или перенести сюда

def page_register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})