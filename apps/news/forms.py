from django import forms
from .models import News


class NewsCreateForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок новости'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Текст новости...'
            }),
            # image обрабатывается отдельно через JS для превью,
            # но класс form-control добавим для единообразия отступов, если нужно
            'image': forms.FileInput(attrs={
                'class': 'd-none', # Скрываем стандартный инпут, используем кастомную область
                'id': 'id_image_input'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Пример простой валидации размера (опционально)
            if image.size > 5 * 1024 * 1024:  # 5 MB
                raise forms.ValidationError("Размер изображения не должен превышать 5 МБ.")
        return image