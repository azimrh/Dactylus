from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Prefetch
from ..models import Category, TextLexeme, LexemeTriplet, GestureRealization, Meaning


def page_category(request, slug):
    category = get_object_or_404(
        Category.objects.annotate(
            words_count=Count(
                'lexemetriplet__text_lexeme',
                filter=Q(lexemetriplet__moderation_status='approved'),
                distinct=True,
            ),
            gestures_count=Count(
                'lexemetriplet__gesture_lexeme',
                filter=Q(lexemetriplet__moderation_status='approved'),
                distinct=True,
            )
        ),
        slug=slug,
    )

    subcategories = category.children.annotate(
        words_count=Count(
            'lexemetriplet__text_lexeme',
            filter=Q(lexemetriplet__moderation_status='approved'),
            distinct=True,
        ),
        gestures_count=Count(
            'lexemetriplet__gesture_lexeme',
            filter=Q(lexemetriplet__moderation_status='approved'),
            distinct=True,
        ),
    )

    # Хлебные крошки
    navigation = []
    current = category
    while current.parent:
        navigation.insert(0, {'name': current.parent.name, 'href': current.parent.get_absolute_url()})
        current = current.parent

    # Одобренные триплеты в категории
    approved_triplets = LexemeTriplet.objects.filter(
        categories=category,
        moderation_status='approved',
    ).select_related('text_lexeme', 'gesture_lexeme', 'meaning')

    # Уникальные текстовые лексемы
    text_lexeme_ids = approved_triplets.values_list('text_lexeme_id', flat=True).distinct()

    # Основной запрос текстовых лексем
    text_lexemes_qs = TextLexeme.objects.filter(
        id__in=text_lexeme_ids,
        moderation_status='approved',
    ).select_related('author').order_by('text')

    # Маппинг text_lexeme -> первый попавшийся gesture_lexeme из триплетов для обложки
    text_to_gesture = {}
    # Маппинг text_lexeme -> первое попавшееся значение (Meaning)
    text_to_meaning = {}

    for triplet in approved_triplets:
        tid = triplet.text_lexeme_id
        if tid not in text_to_gesture:
            text_to_gesture[tid] = triplet.gesture_lexeme_id
        if tid not in text_to_meaning:
            text_to_meaning[tid] = triplet.meaning

    # Реализации для превью
    gesture_ids = list(set(text_to_gesture.values()))
    realizations_map = {}
    if gesture_ids:
        for real in GestureRealization.objects.filter(
                gesture_lexeme_id__in=gesture_ids,
                is_primary=True,
                moderation_status='approved',
        ):
            if real.gesture_lexeme_id not in realizations_map:
                realizations_map[real.gesture_lexeme_id] = real

    paginator = Paginator(text_lexemes_qs, 24)
    page = request.GET.get('page')
    text_lexemes = paginator.get_page(page)

    for lexeme in text_lexemes:
        # 1. Картинка жеста
        gesture_id = text_to_gesture.get(lexeme.id)
        lexeme.primary_image = None
        if gesture_id:
            real = realizations_map.get(gesture_id)
            if real:
                lexeme.primary_image = real.gif_mini.url or real.gif.url or (real.image.url if real.image else None)

        # 2. Значение для превью
        lexeme.preview_meaning = text_to_meaning.get(lexeme.id)

    return render(request, 'dictionary/dictionary.html', {
        'category': category,
        'navigation': navigation,
        'subcategories': subcategories,
        'text_lexemes': text_lexemes,
    })