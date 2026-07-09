from django.db.models import Count, Q, Prefetch
from django.shortcuts import render
from apps.dictionary.models import Category, LexemeTriplet


def page_dictionary(request):
    categories = Category.objects.filter(parent=None).prefetch_related(
        'children',
        Prefetch(
            'lexemetriplet_set',
            queryset=LexemeTriplet.objects.filter(
                moderation_status='approved'
            ).select_related('text_lexeme').order_by('text_lexeme__text')
        )
    ).annotate(
        subcategories_count=Count('children', distinct=True),
        words_count=Count(
            'lexemetriplet__text_lexeme',
            filter=Q(lexemetriplet__moderation_status='approved'),
            distinct=True
        ),
        gestures_count=Count(
            'lexemetriplet__gesture_lexeme',
            filter=Q(lexemetriplet__moderation_status='approved'),
            distinct=True
        ),
    ).order_by('order', 'name')

    return render(request, 'dictionary/dictionary.html', {
        'categories': categories,
        'category': None,
    })