from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Расширенная форма регистрации с полем hearing_status.
    """
    hearing_status = forms.ChoiceField(
        choices=User.HEARING_STATUS_CHOICES,
        initial='hearing',
        label='Статус слуха',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'hearing_status', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем классы к стандартным полям
        self.fields['username'].widget.attrs.update({'class': 'form-input'})
        self.fields['password1'].widget.attrs.update({'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.hearing_status = self.cleaned_data['hearing_status']
        # По умолчанию роль 'user'
        user.role = 'user'

        if commit:
            user.save()
        return user
