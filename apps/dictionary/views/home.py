from django.shortcuts import render

from apps.dictionary.models import (
    News, User,
    Category,
    TextLexeme,
    GestureLexeme,
    GestureRealization
)


def page_home(request):
    categories = Category.objects.filter(parent=None)[:6]
    news = News.objects.filter(is_published=True)[:3]

    stats = {
        'gestures': GestureLexeme.objects.filter(moderation_status='approved').count(),
        'words': TextLexeme.objects.filter(moderation_status='approved').count(),
        'users': User.objects.count(),
        'videos': GestureRealization.objects.filter(moderation_status='approved').count(),
    }

    context = {
        'categories': categories,
        'news': news,
        'stats': stats,
    }
    return render(request, 'dictionary/home.html', context)
