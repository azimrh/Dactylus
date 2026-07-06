from django.shortcuts import render
from apps.users.models import User
from apps.dictionary.models import Category, TextLexeme, GestureLexeme, GestureRealization, LexemeTriplet
from apps.news.models import News


def page_home(request):
    categories = Category.objects.filter(parent=None)[:6]
    news = News.objects.filter(is_published=True)[:3]
    stats = {
        'gestures': GestureLexeme.objects.filter(
            triplets__moderation_status='approved'
        ).distinct().count(),

        'words': TextLexeme.objects.filter(moderation_status='approved').count(),
        'users': User.objects.count(),
        'videos': GestureRealization.objects.filter(moderation_status='approved').count(),
    }
    return render(request, 'dictionary/home.html', {
        'categories': categories,
        'news': news,
        'stats': stats,
    })