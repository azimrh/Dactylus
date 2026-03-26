from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Prefetch

from ..models.lexical import (
    Category,
    TextLexeme, LexemePair,
    GestureLexeme, GestureRealization
)


def category(request, slug):
    """Страница категории — подкатегории и слова."""
    category = get_object_or_404(
        Category.objects.annotate(
            words_count=Count('textlexeme', filter=Q(textlexeme__is_published=True), distinct=True),
            gestures_count=Count('gesturelexeme', filter=Q(gesturelexeme__is_published=True), distinct=True),
        ),
        slug=slug
    )

    subcategories = category.children.annotate(
        words_count=Count('textlexeme', filter=Q(textlexeme__is_published=True), distinct=True),
        gestures_count=Count('gesturelexeme', filter=Q(gesturelexeme__is_published=True), distinct=True),
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

    text_lexemes_list = list(TextLexeme.objects.filter(
        categories=category,
        is_published=True
    ).select_related('author').prefetch_related('meanings'))

    pairs = LexemePair.objects.filter(
        text_lexeme_type__model='textlexeme',
        text_lexeme_id__in=[l.id for l in text_lexemes_list]
    )

    pairs_map = {}
    gesture_ids_by_type = {}

    for pair in pairs:
        pairs_map.setdefault(pair.text_lexeme_id, []).append(pair)

        type_id = pair.gesture_lexeme_type_id
        gesture_ids_by_type.setdefault(type_id, []).append(pair.gesture_lexeme_id)

    gesture_realizations = GestureRealization.objects.filter(
        lexeme_type__model__in=['gesturelexeme', 'gesturelexemecompose'],
        lexeme_id__in=[
            gid for ids in gesture_ids_by_type.values() for gid in ids
        ],
        is_primary=True,
        moderation_status='approved'
    )

    realizations_map = {}

    for r in gesture_realizations:
        key = (r.lexeme_type_id, r.lexeme_id)
        realizations_map.setdefault(key, []).append(r)

    for lexeme in text_lexemes_list:
        lexeme.primary_image = None

        for pair in pairs_map.get(lexeme.id, []):
            key = (pair.gesture_lexeme_type_id, pair.gesture_lexeme_id)

            realizations = realizations_map.get(key)
            if not realizations:
                continue

            r = realizations[0]

            if r.gif:
                lexeme.primary_image = r.gif.url
                break
            if r.image:
                lexeme.primary_image = r.image.url
                break

    paginator = Paginator(text_lexemes_list, 24)
    page = request.GET.get('page')
    text_lexemes = paginator.get_page(page)

    return render(request, 'dictionary/dictionary.html', {
        'category': category,
        'navigation': navigation,
        'subcategories': subcategories,
        'text_lexemes': text_lexemes
    })
