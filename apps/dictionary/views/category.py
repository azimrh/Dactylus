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

    text_lexemes_list = TextLexeme.objects.filter(
        categories=category,
        is_published=True
    ).select_related('author').prefetch_related('meanings').order_by('text')

    lexeme_ids = list(text_lexemes_list.values_list('id', flat=True))
    text_ct = ContentType.objects.get_for_model(TextLexeme)
    pairs = LexemePair.objects.filter(
        text_lexeme_type=text_ct,
        text_lexeme_id__in=lexeme_ids
    ).select_related('gesture_lexeme_type')

    paginator = Paginator(text_lexemes_list, 24)
    page = request.GET.get('page')
    text_lexemes = paginator.get_page(page)

    return render(request, 'dictionary/dictionary.html', {
        'category': category,
        'navigation': navigation,
        'subcategories': subcategories,
        'text_lexemes': text_lexemes
    })
