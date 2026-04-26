from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Prefetch

from ..models.lexical import (
    Category,
    TextLexeme,
    LexemePair,
    GestureLexeme,
    GestureRealization,
)


def page_category(request, slug):
    """Страница категории — подкатегории и пары текст–жест."""
    category = get_object_or_404(
        Category.objects.annotate(
            words_count=Count(
                'lexemepair__text_lexeme',
                filter=Q(lexemepair__moderation_status='approved'),
                distinct=True,
            ),
            gestures_count=Count(
                'lexemepair__gesture_lexeme',
                filter=Q(lexemepair__moderation_status='approved'),
                distinct=True,
            ),
        ),
        slug=slug,
    )

    subcategories = category.children.annotate(
        words_count=Count(
            'lexemepair__text_lexeme',
            filter=Q(lexemepair__moderation_status='approved'),
            distinct=True,
        ),
        gestures_count=Count(
            'lexemepair__gesture_lexeme',
            filter=Q(lexemepair__moderation_status='approved'),
            distinct=True,
        ),
    )

    # Хлебные крошки
    navigation = []
    current = category
    while current.parent:
        navigation.insert(
            0,
            {
                'name': current.parent.name,
                'href': current.parent.get_absolute_url(),
            },
        )
        current = current.parent

    # Одобренные пары в категории
    approved_pairs = LexemePair.objects.filter(
        categories=category,
        moderation_status='approved',
    )

    # Уникальные текстовые лексемы из этих пар
    text_lexeme_ids = (
        approved_pairs.values_list('text_lexeme_id', flat=True)
        .distinct()
    )

    text_lexemes_qs = (
        TextLexeme.objects.filter(
            id__in=text_lexeme_ids,
            moderation_status='approved',
        )
        .select_related('author')
        .prefetch_related('meanings')
        .order_by('text')
    )

    # Сопоставление text_lexeme → первая попавшаяся жестовая лемма (для обложки)
    text_to_gesture = {}
    for pair in approved_pairs.filter(
        text_lexeme_id__in=text_lexeme_ids
    ).select_related('gesture_lexeme'):
        if pair.text_lexeme_id not in text_to_gesture:
            text_to_gesture[pair.text_lexeme_id] = pair.gesture_lexeme_id

    # Первичные реализации всех задействованных жестов
    gesture_ids = list(text_to_gesture.values())
    realizations_map = {}
    if gesture_ids:
        for real in GestureRealization.objects.filter(
            gesture_lexeme_id__in=gesture_ids,
            is_primary=True,
            moderation_status='approved',
        ):
            if real.gesture_lexeme_id not in realizations_map:
                realizations_map[real.gesture_lexeme_id] = real

    # Пагинация
    paginator = Paginator(text_lexemes_qs, 24)
    page = request.GET.get('page')
    text_lexemes = paginator.get_page(page)

    # Добавляем primary_image каждому объекту на странице
    for lexeme in text_lexemes:
        gesture_id = text_to_gesture.get(lexeme.id)
        lexeme.primary_image = None
        if gesture_id:
            real = realizations_map.get(gesture_id)
            if real:
                if real.gif:
                    lexeme.primary_image = real.gif.url
                elif real.image:
                    lexeme.primary_image = real.image.url

    return render(
        request,
        'dictionary/dictionary.html',
        {
            'category': category,
            'navigation': navigation,
            'subcategories': subcategories,
            'text_lexemes': text_lexemes,
        },
    )