from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from apps.dictionary.models import (
    Category,
    TextLexeme, LexemePair, GestureRealization
)
from .base import group_required


def page_dictionary(request):
    """Главная страница словаря — список корневых категорий."""
    categories = Category.objects.filter(
        parent=None
    ).prefetch_related('children').annotate(
        subcategories_count=Count('children', distinct=True),
        words_count=Count('textlexeme',
            filter=Q(textlexeme__moderation_status='approved'),
            distinct=True
        ),
        gestures_count=Count('gesturelexeme',
            filter=Q(textlexeme__moderation_status='approved'),
            distinct=True
        ),
    )

    return render(request, 'dictionary/dictionary.html', {
        'categories': categories,
        'category': None,
    })

def page_text_lexeme(request, slug):
    lemma = get_object_or_404(
        TextLexeme.objects.prefetch_related('meanings', 'categories'),
        slug=slug
    )

    # Получаем связанные жесты через LexemePair (прямая связь ForeignKey)
    lexeme_pairs = LexemePair.objects.filter(
        text_lexeme=lemma
    ).select_related('gesture_lexeme')

    # Собираем жесты
    gesture_lexemes = [pair.gesture_lexeme for pair in lexeme_pairs]

    # Получаем ID всех жестов для поиска реализаций
    all_gesture_ids = [g.id for g in gesture_lexemes]

    gesture_realizations = GestureRealization.objects.filter(
        gesture_lexeme_id__in=all_gesture_ids,
        moderation_status='approved'
    ).select_related('author', 'moderated_by', 'gesture_lexeme')

    # Группировка по жестам
    main_gesture = gesture_realizations.first()
    other_gestures = list(gesture_realizations.exclude(
        id=main_gesture.id if main_gesture else None
    ))

    meanings = list(lemma.meanings.all())
    synonyms = TextLexeme.objects.filter(
        meanings__in=meanings,
        moderation_status='approved'
    ).exclude(id=lemma.id).distinct()[:10]

    synonyms_by_meaning = {}
    for meaning in meanings:
        words = TextLexeme.objects.filter(
            meanings=meaning,
            moderation_status='approved'
        ).exclude(id=lemma.id).distinct()[:5]
        if words:
            synonyms_by_meaning[meaning] = words

    # Навигация
    categories = lemma.categories.all()
    navigation = []
    if categories:
        current = categories.first()
        path = []
        while current:
            path.insert(0, current)
            current = current.parent
        for cat in path:
            navigation.append({
                'name': cat.name,
                'href': reverse('category', kwargs={'slug': cat.slug})
            })

    context = {
        'lemma': lemma,
        'meanings': meanings,
        'synonyms': synonyms,
        'synonyms_by_meaning': synonyms_by_meaning,
        'main_gesture': main_gesture,
        'other_gestures': other_gestures,
        'gesture_realizations': gesture_realizations,
        'gesture_lexemes': gesture_lexemes,
        'categories': categories,
        'navigation': navigation,
    }
    return render(request, 'dictionary/text_lexeme.html', context)
