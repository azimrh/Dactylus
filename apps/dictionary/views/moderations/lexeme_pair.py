from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse

from apps.dictionary.models import LexemePair
from ..base import group_required

@login_required
@group_required('moderator')
def moderation_lexeme_pair(request, pk):
    """Модерация пары текст-жест"""
    pair = get_object_or_404(
        LexemePair.objects.select_related(
            'text_lexeme',
            'gesture_lexeme',
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
            word_id = request.POST.get('word_id')
            category_ids = request.POST.getlist('category_ids')

            if word_id:
                pair.text_lexeme_id = word_id

            if category_ids:
                pair.categories.set(category_ids)

            pair.moderation_status = 'approved'
            pair.save()

            messages.success(request, 'Пара одобрена')
            return redirect(reverse('moderation') + '#pairs')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            pair.delete()
            messages.success(request, f'Пара отклонена: {reason}')
            return redirect(reverse('moderation') + '#pairs')

    context = {
        'pair': pair,
        'current_categories': list(pair.categories.values('id', 'name')),
    }

    return render(request, 'dictionary/moderation/pair.html', context)