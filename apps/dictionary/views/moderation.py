from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q, Prefetch
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models.lexical import (
    Category,
    TextLexeme, LexemePair,
    GestureLexeme, GestureRealization
)
from ..models.semantic import Meaning


@login_required
def moderation(request):
    """Список пар на модерации"""
    pending_count = LexemePair.objects.filter(is_auto_meaning=True).count()
    approved_count = LexemePair.objects.filter(is_auto_meaning=False).count()
    rejected_count = 0

    pending_pairs = LexemePair.objects.filter(
        is_auto_meaning=True
    ).select_related(
        'text_lexeme',
        'gesture_lexeme',
        'created_by'
    ).order_by('-created_at')

    paginator = Paginator(pending_pairs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'pending_pairs': page_obj,
    }

    return render(request, 'dictionary/moderation.html', context)


@login_required
def moderation_detail(request, pair_id):
    """Детальная страница редактирования пары"""
    pair = get_object_or_404(
        LexemePair.objects.select_related(
            'text_lexeme',
            'gesture_lexeme',
            'meaning',
            'created_by'
        ).prefetch_related(
            'text_lexeme__categories',
            'gesture_lexeme__realizations'
        ),
        id=pair_id,
        is_auto_meaning=True
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

            pair.is_auto_meaning = False
            pair.save()

            messages.success(request, 'Пара одобрена')
            return redirect('moderation')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            pair.delete()
            messages.success(request, f'Пара отклонена: {reason}')
            return redirect('moderation')

    # Данные для AJAX-поиска
    context = {
        'pair': pair,
        'current_categories': list(pair.text_lexeme.categories.values('id', 'name')),
    }

    return render(request, 'dictionary/moderation_detail.html', context)
