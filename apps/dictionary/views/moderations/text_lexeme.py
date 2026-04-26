from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.text import slugify

from apps.dictionary.models import TextLexeme
from ..base import group_required


@login_required
@group_required('moderator')
def moderation_text_lexeme(request, pk):
    """Модерация текстовой леммы"""
    lexeme = get_object_or_404(TextLexeme, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            new_text = request.POST.get('text')
            meaning_ids = request.POST.getlist('meaning_ids')

            # Проверка на дубликат при изменении текста
            if new_text and new_text != lexeme.text:
                new_slug = slugify(new_text)

                # Проверяем, не существует ли уже слова с таким slug
                if TextLexeme.objects.filter(slug=new_slug).exclude(pk=lexeme.pk).exists():
                    messages.error(request, f'Слово "{new_text}" уже существует в словаре')
                    return redirect('moderation-text', pk=pk)

                lexeme.text = new_text
                lexeme.slug = new_slug

            # Обновляем значения
            if meaning_ids:
                lexeme.meanings.set(meaning_ids)

            lexeme.moderation_status = 'approved'
            lexeme.save()
            messages.success(request, f'Слово "{lexeme.text}" одобрено')
            return redirect('moderation')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            lexeme.moderation_status = 'rejected'
            lexeme.save()
            messages.success(request, f'Слово "{lexeme.text}" отклонено: {reason}')
            return redirect('moderation')

    context = {
        'lexeme': lexeme,
        'current_meanings': list(lexeme.meanings.values('id', 'description')),
    }
    return render(request, 'dictionary/moderation/#words', context)
