from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from apps.dictionary.models import (
    Meaning,
    TextLexeme, GestureLexeme, LexemePair, GestureRealization
)
from ..base import group_required


@login_required
@group_required('moderator')
def moderation_text_lexeme(request, pk):
    """Модерация текстовой леммы"""
    lexeme = get_object_or_404(TextLexeme, pk=pk, moderation_status='pending')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            new_text = request.POST.get('text')
            category_ids = request.POST.getlist('category_ids')

            # Проверка на дубликат при изменении текста
            if new_text and new_text != lexeme.text:
                from django.utils.text import slugify
                new_slug = slugify(new_text)

                # Проверяем, не существует ли уже слова с таким slug
                if TextLexeme.objects.filter(slug=new_slug).exclude(pk=lexeme.pk).exists():
                    messages.error(request, f'Слово "{new_text}" уже существует в словаре')
                    return redirect('moderation-text', pk=pk)

                lexeme.text = new_text
                lexeme.slug = new_slug

            # Обновляем категории
            if category_ids:
                lexeme.categories.set(category_ids)

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
        'current_categories': list(lexeme.categories.values('id', 'name')),
    }
    return render(request, 'dictionary/moderation/text_lexeme.html', context)


@login_required
@group_required('moderator')
def moderation_gesture_lexeme(request, pk):
    """Модерация жестовой леммы"""
    lexeme = get_object_or_404(GestureLexeme, pk=pk, moderation_status='pending')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            new_text = request.POST.get('text')
            category_ids = request.POST.getlist('category_ids')

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

            # Обновляем категории
            if category_ids:
                lexeme.categories.set(category_ids)

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
        'current_categories': list(lexeme.categories.values('id', 'name')),
    }
    return render(request, 'dictionary/moderation/gesture_lexeme.html', context)


@login_required
@group_required('moderator')
def moderation_meaning(request, pk):
    """Модерация смысла"""
    meaning = get_object_or_404(Meaning, pk=pk, moderation_status='pending')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            new_description = request.POST.get('description', '').strip()

            if new_description:
                meaning.description = new_description

            meaning.moderation_status = 'approved'
            meaning.save()  # <-- всегда сохраняем статус

            messages.success(request, 'Смысл одобрен')
            return redirect('moderation')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            meaning.delete()
            messages.success(request, f'Смысл отклонен: {reason}')
            return redirect('moderation')

    return render(request, 'dictionary/moderation/meaning.html', {
        'meaning': meaning,
    })


@login_required
@group_required('moderator')
def moderation_video(request, pk):
    """Модерация видео (GestureRealization)"""
    video = get_object_or_404(GestureRealization, pk=pk, moderation_status='pending')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            video.moderation_status = 'approved'
            video.moderated_by = request.user
            video.save()
            messages.success(request, f'Видео для "{video.gesture_lexeme.text}" одобрено')
            return redirect('moderation')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            video.moderation_status = 'rejected'
            video.moderated_by = request.user
            video.moderation_comment = reason
            video.save()
            messages.success(request, f'Видео отклонено: {reason}')
            return redirect('moderation')

    return render(request, 'dictionary/moderation/video.html', {
        'video': video,
    })

@login_required
@group_required('moderator')
def moderation_pair(request, pk):
    """Модерация пары текст-жест"""
    pair = get_object_or_404(
        LexemePair.objects.select_related(
            'text_lexeme',
            'gesture_lexeme',
            'created_by'
        ).prefetch_related(
            'text_lexeme__categories',
            'gesture_lexeme__realizations'
        ),
        pk=pk
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            word_id = request.POST.get('word_id')
            meaning_id = request.POST.get('meaning_id')
            category_ids = request.POST.getlist('category_ids')

            if word_id:
                pair.text_lexeme_id = word_id
            if meaning_id:
                pair.meaning_id = meaning_id
            if category_ids:
                pair.text_lexeme.categories.set(category_ids)
                pair.gesture_lexeme.categories.set(category_ids)

            pair.moderation_status = 'approved'
            pair.save()

            messages.success(request, 'Пара одобрена')
            return redirect('moderation')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            pair.delete()
            messages.success(request, f'Пара отклонена: {reason}')
            return redirect('moderation')

    context = {
        'pair': pair,
        'current_categories': list(pair.text_lexeme.categories.values('id', 'name')),
    }

    return render(request, 'dictionary/moderation/pair.html', context)
