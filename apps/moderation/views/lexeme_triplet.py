from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from apps.dictionary.models import LexemeTriplet, Category, TextLexeme, Meaning, GestureLexeme
from apps.dictionary.views._base import group_required


@login_required
@group_required('moderator')
def moderation_lexeme_triplet(request, pk):
    """Модерация триплета текст-значение-жест"""
    triplet = get_object_or_404(
        LexemeTriplet.objects.select_related(
            'text_lexeme',
            'gesture_lexeme',
            'meaning',
            'created_by'
        ).prefetch_related(
            'categories',
            'gesture_lexeme__realizations'
        ),
        pk=pk
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            # 1. Обновляем Категории
            category_ids = request.POST.getlist('category_ids')
            if category_ids:
                triplet.categories.set(category_ids)

            # 2. Обновляем Значение (Meaning), если оно было изменено в UI
            new_meaning_id = request.POST.get('meaning_id')
            if new_meaning_id:
                try:
                    # Проверяем, существует ли такое значение
                    new_meaning = Meaning.objects.get(id=new_meaning_id)
                    triplet.meaning = new_meaning
                except Meaning.DoesNotExist:
                    messages.error(request, 'Выбранное значение не найдено')
                    return redirect(reverse('moderation_lexeme_triplet', kwargs={'pk': pk}))

            # 3. Обновляем Текстовую лемму (Word), если она была изменена в UI
            new_word_id = request.POST.get('word_id')
            if new_word_id:
                try:
                    new_text_lexeme = TextLexeme.objects.get(id=new_word_id)
                    triplet.text_lexeme = new_text_lexeme
                except TextLexeme.DoesNotExist:
                    messages.error(request, 'Выбранное слово не найдено')
                    return redirect(reverse('moderation_lexeme_triplet', kwargs={'pk': pk}))

            # Примечание: Жест (GestureLexeme) обычно не меняют через эту форму,
            # так как он привязан к видео. Если нужно менять и его, добавьте аналогичную логику.

            triplet.moderation_status = 'approved'
            triplet.save()

            messages.success(request, 'Триплет одобрен')
            return redirect(reverse('moderation') + '#triplets')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            triplet.moderation_status = 'rejected'
            triplet.save()

            messages.success(request, f'Триплет отклонен: {reason}')
            return redirect(reverse('moderation') + '#triplets')

    context = {
        'triplet': triplet,
        'current_categories': list(triplet.categories.values('id', 'name')),
        'all_categories': Category.objects.all().order_by('name'),
    }
    return render(request, 'moderation/triplet.html', context)