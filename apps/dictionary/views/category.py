from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Prefetch

from ..models.lexical import (
    Category,
    TextLexeme, LexemePair,
    GestureLexeme, GestureRealization
)


def page_category(request, slug):
    """Страница категории — подкатегории и слова."""
    category = get_object_or_404(
        Category.objects.annotate(
            words_count=Count('textlexeme',
                filter=Q(textlexeme__moderation_status='approved'),
                distinct=True
            ),
            gestures_count=Count('gesturelexeme',
                filter=Q(gesturelexeme__moderation_status='approved'),
                distinct=True
            ),
        ),
        slug=slug
    )

    subcategories = category.children.annotate(
        words_count=Count('textlexeme',
            filter=Q(textlexeme__moderation_status='approved'),
            distinct=True
        ),
        gestures_count=Count('gesturelexeme',
            filter=Q(gesturelexeme__moderation_status='approved'),
            distinct=True
        ),
    )

    # Навигация

    navigation = []
    current = category
    while current.parent:
        navigation.insert(0, {
            'name': current.parent.name,
            'href': current.parent.get_absolute_url()
        })
        current = current.parent

    # Слова в категории

    text_lexemes_list = list(TextLexeme.objects.filter(
        categories=category,
        moderation_status='approved'
    ).select_related('author').prefetch_related('meanings'))

    pairs = LexemePair.objects.filter(
        text_lexeme__in=text_lexemes_list
    ).select_related('gesture_lexeme')

    pairs_map = {}
    gesture_ids = []

    for pair in pairs:
        pairs_map.setdefault(pair.text_lexeme_id, []).append(pair)
        gesture_ids.append(pair.gesture_lexeme_id)

    # Реализации жестов

    gesture_realizations = GestureRealization.objects.filter(
        gesture_lexeme_id__in=gesture_ids,
        is_primary=True,
        moderation_status='approved'
    )

    realizations_map = {}

    for r in gesture_realizations:
        realizations_map.setdefault(r.gesture_lexeme_id, []).append(r)

    for lexeme in text_lexemes_list:
        lexeme.primary_image = None

        for pair in pairs_map.get(lexeme.id, []):
            realizations = realizations_map.get(pair.gesture_lexeme_id)
            if not realizations:
                continue

            r = realizations[0]

            if r.gif:
                lexeme.primary_image = r.gif.url
                break
            if r.image:
                lexeme.primary_image = r.image.url
                break

    # Пагинация

    paginator = Paginator(text_lexemes_list, 24)
    page = request.GET.get('page')
    text_lexemes = paginator.get_page(page)

    return render(request, 'dictionary/dictionary.html', {
        'category': category,
        'navigation': navigation,
        'subcategories': subcategories,
        'text_lexemes': text_lexemes
    })

