from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from apps.dictionary.models import Category, TextLexeme, LexemeTriplet, GestureRealization
from apps.personal.models import Personal
from ._base import group_required


def page_text_lexeme(request, slug):
    lemma = get_object_or_404(TextLexeme, slug=slug)

    # 1. Сбор triplets по text_lexeme
    triplets = LexemeTriplet.objects.filter(
        text_lexeme=lemma,
        moderation_status='approved'
    ).select_related('meaning', 'gesture_lexeme')

    # 2. Группировка по meanings
    meanings_data = {}
    for t in triplets:
        if t.meaning not in meanings_data:
            meanings_data[t.meaning] = {
                'triplet': t,  # ← первый triplet для этого meaning
                'triplets': [],
                'gestures': [],
                'synonyms': [],
            }
        meanings_data[t.meaning]['triplets'].append(t)

    # Собираем реализации жестов и синонимы для каждого meaning
    for meaning, data in meanings_data.items():
        gesture_ids = [t.gesture_lexeme_id for t in data['triplets'] if t.gesture_lexeme_id]
        if gesture_ids:
            data['gestures'] = list(GestureRealization.objects.filter(
                gesture_lexeme_id__in=gesture_ids,
                moderation_status='approved'
            ).select_related('author', 'gesture_lexeme'))

        # Синонимы
        synonym_triplets = LexemeTriplet.objects.filter(
            meaning=meaning,
            moderation_status='approved'
        ).exclude(text_lexeme=lemma).select_related('text_lexeme')

        seen_ids = set()
        data['synonyms'] = []
        for t in synonym_triplets:
            if t.text_lexeme_id not in seen_ids:
                seen_ids.add(t.text_lexeme_id)
                data['synonyms'].append(t.text_lexeme)

        # Проверка в личном словаре — для КАЖДОГО triplet отдельно
        data['in_personal'] = False
        data['triplet_id'] = data['triplet'].id
        if request.user.is_authenticated:
            data['in_personal'] = Personal.objects.filter(
                user=request.user,
                lexeme_triplet_id=data['triplet'].id
            ).exists()

    # Категории
    categories = Category.objects.filter(
        lexemetriplet__text_lexeme=lemma,
        lexemetriplet__moderation_status='approved'
    ).distinct()

    navigation = []
    if first_cat := categories.first():
        current = first_cat
        while current:
            navigation.insert(0, {
                'name': current.name,
                'href': reverse('category', kwargs={'slug': current.slug})
            })
            current = current.parent

    return render(request, 'dictionary/text_lexeme.html', {
        'lemma': lemma,
        'meanings_data': meanings_data,
        'categories': categories,
        'navigation': navigation,
    })