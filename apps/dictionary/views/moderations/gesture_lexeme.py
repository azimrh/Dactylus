from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from apps.dictionary.models import GestureLexeme
from ..base import group_required

@login_required
@group_required('moderator')
def moderation_gesture_lexeme(request, pk):
    """Модерация жестовой леммы"""
    lexeme = get_object_or_404(GestureLexeme, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            new_text = request.POST.get('text')
            meaning_ids = request.POST.getlist('meaning_ids')

            # Проверка на дубликат при изменении текста
            if new_text and new_text != lexeme.text:
                from django.utils.text import slugify
                new_slug = slugify(new_text)

                # Проверяем, не существует ли уже жеста с таким slug
                if GestureLexeme.objects.filter(slug=new_slug).exclude(pk=lexeme.pk).exists():
                    messages.error(request, f'Жест "{new_text}" уже существует в словаре')
                    return redirect('moderation-gesture', pk=pk)

                lexeme.text = new_text
                lexeme.slug = new_slug

            # Обновляем значения
            if meaning_ids:
                lexeme.meanings.set(meaning_ids)

            lexeme.moderation_status = 'approved'
            lexeme.save()
            messages.success(request, f'Жест "{lexeme.text}" одобрен')
            return redirect('moderation')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            lexeme.moderation_status = 'rejected'
            lexeme.save()
            messages.success(request, f'Жест "{lexeme.text}" отклонен: {reason}')
            return redirect('moderation')

    context = {
        'lexeme': lexeme,
        'current_meanings': list(lexeme.meanings.values('id', 'description')),
    }
    return render(request, 'dictionary/moderation/#gestures', context)
