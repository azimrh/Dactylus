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


def dictionary(request):
    """Главная страница словаря — список корневых категорий."""
    categories = Category.objects.filter(
        parent=None
    ).prefetch_related('children').annotate(
        subcategories_count=Count('children', distinct=True),
        words_count=Count('textlexeme', filter=Q(textlexeme__is_published=True), distinct=True),
        gestures_count=Count('gesturelexeme', filter=Q(gesturelexeme__is_published=True), distinct=True),
    )

    return render(request, 'dictionary/dictionary.html', {
        'categories': categories,
        'category': None,
    })

def text_lexeme(request, slug):
    lemma = get_object_or_404(
        TextLexeme.objects.prefetch_related('meanings', 'categories'),
        slug=slug,
        is_published=True
    )

    # Получаем связанные жесты через LexemePair
    lexeme_pairs = LexemePair.objects.filter(
        text_lexeme_type__model='textlexeme',
        text_lexeme_id=lemma.id
    )

    # Собираем ID жестов по типам
    gesture_ids_by_type = {}
    for pair in lexeme_pairs:
        type_id = pair.gesture_lexeme_type_id
        if type_id not in gesture_ids_by_type:
            gesture_ids_by_type[type_id] = []
        gesture_ids_by_type[type_id].append(pair.gesture_lexeme_id)

    # Загружаем жесты отдельно по типам
    gesture_lexemes = []
    for type_id, ids in gesture_ids_by_type.items():
        ct = ContentType.objects.get_for_id(type_id)
        model_class = ct.model_class()
        if model_class:
            gestures = model_class.objects.filter(id__in=ids)
            gesture_lexemes.extend(list(gestures))

    # Получаем ID всех жестов для поиска реализаций
    all_gesture_ids = [g.id for g in gesture_lexemes]

    gesture_realizations = GestureRealization.objects.filter(
        lexeme_type__model__in=['gesturelexeme', 'gesturelexemecompose'],
        lexeme_id__in=all_gesture_ids,
        moderation_status='approved'
    ).select_related('author', 'moderated_by')

    # Группировка по жестам
    main_gesture = gesture_realizations.first()
    other_gestures = list(gesture_realizations.exclude(
        id=main_gesture.id if main_gesture else None
    ))

    meanings = list(lemma.meanings.all())
    synonyms = TextLexeme.objects.filter(
        meanings__in=meanings,
        is_published=True
    ).exclude(id=lemma.id).distinct()[:10]

    synonyms_by_meaning = {}
    for meaning in meanings:
        words = TextLexeme.objects.filter(
            meanings=meaning,
            is_published=True
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
