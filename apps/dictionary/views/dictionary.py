from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q, Prefetch
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from apps.dictionary.models import (
    Category,
    TextLexeme, LexemePair, GestureRealization,
    Personal
)
from .base import group_required


def page_dictionary(request):
    """Главная страница словаря — список корневых категорий."""
    categories = Category.objects.filter(
        parent=None
    ).prefetch_related(
        'children',
        Prefetch(
            'lexemepair_set',
            queryset=LexemePair.objects.filter(
                moderation_status='approved'
            ).select_related('text_lexeme').order_by('text_lexeme__text')
        )
    ).annotate(
        subcategories_count=Count('children', distinct=True),
        words_count=Count(
            'lexemepair__text_lexeme',
            filter=Q(lexemepair__moderation_status='approved'),
            distinct=True
        ),
        gestures_count=Count(
            'lexemepair__gesture_lexeme',
            filter=Q(lexemepair__moderation_status='approved'),
            distinct=True
        ),
    )

    return render(request, 'dictionary/dictionary.html', {
        'categories': categories,
        'category': None,
    })


def page_text_lexeme(request, slug):
    lemma = get_object_or_404(
        TextLexeme.objects.prefetch_related('meanings'),
        slug=slug
    )

    # Пары с жестами
    lexeme_pairs = LexemePair.objects.filter(
        text_lexeme=lemma,
        moderation_status='approved'
    ).select_related('gesture_lexeme')

    # Реализации жестов
    gesture_ids = [pair.gesture_lexeme_id for pair in lexeme_pairs]
    gesture_realizations = GestureRealization.objects.filter(
        gesture_lexeme_id__in=gesture_ids,
        moderation_status='approved'
    ).select_related('author', 'gesture_lexeme')

    main_gesture = gesture_realizations.first()

    # Значения и синонимы
    meanings = list(lemma.meanings.all())
    synonyms_by_meaning = {}
    for meaning in meanings:
        words = TextLexeme.objects.filter(
            meanings=meaning,
            moderation_status='approved'
        ).exclude(id=lemma.id)[:5]
        if words:
            synonyms_by_meaning[meaning] = words

    # Категории и навигация
    categories = Category.objects.filter(
        lexemepair__text_lexeme=lemma,
        lexemepair__moderation_status='approved'
    ).distinct()

    navigation = []
    if first := categories.first():
        current = first
        while current:
            navigation.insert(0, {
                'name': current.name,
                'href': reverse('category', kwargs={'slug': current.slug})
            })
            current = current.parent

    lexeme_pair = lexeme_pairs.first()
    lexeme_pair_id = lexeme_pair.id if lexeme_pair else None

    # Проверка, есть ли в личном словаре
    in_personal = False
    if request.user.is_authenticated and lexeme_pair_id:
        in_personal = Personal.objects.filter(
            user=request.user,
            lexeme_pair_id=lexeme_pair_id
        ).exists()

    return render(request, 'dictionary/text_lexeme.html', {
        'lemma': lemma,
        'meanings': meanings,
        'synonyms_by_meaning': synonyms_by_meaning,
        'main_gesture': main_gesture,
        'gesture_realizations': gesture_realizations,
        'categories': categories,
        'navigation': navigation,
        'lexeme_pair_id': lexeme_pair_id,
        'in_personal': in_personal,
    })
