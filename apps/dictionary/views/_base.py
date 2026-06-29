from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import login

from apps.dictionary.forms import CustomUserCreationForm

def group_required(*group_names):
    def in_groups(user):
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if user.groups.filter(name__in=group_names).exists():
                return True
        return False

    return user_passes_test(
        in_groups,
        login_url='login',
        redirect_field_name='next'
    )


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
    return render(request, 'dictionary/register.html', {'form': form})
