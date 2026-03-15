from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm
from .models import (
    News, User,
    Category,
    TextLexeme, TextLexemeCompose,
    GestureLexeme, GestureLexemeCompose,
    GestureRealization
)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'dictionary/register.html', {'form': form})


def index(request):
    categories = Category.objects.filter(parent=None)[:6]
    news = News.objects.filter(is_published=True)[:3]

    stats = {
        'gestures': GestureLexeme.objects.filter(is_published=True).count(),
        'words': TextLexeme.objects.filter(is_published=True).count(),
        'users': User.objects.count(),
        'videos': GestureRealization.objects.filter(moderation_status='approved').count(),
    }

    context = {
        'categories': categories,
        'news': news,
        'stats': stats,
    }
    return render(request, 'dictionary/index.html', context)


def dictionary(request):
    categories = Category.objects.filter(parent=None).prefetch_related('children')
    return render(request, 'dictionary/dictionary.html', {'categories': categories})

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)

    navigation = []
    current = category
    while current.parent:
        navigation.insert(0, {
            'name': current.parent.name,
            'href': reverse('category', kwargs={'slug': current.parent.slug})
        })
        current = current.parent

    text_lexemes = TextLexeme.objects.filter(
        categories=category,
        is_published=True
    ).prefetch_related('meanings')

    subcategories = category.children.all()

    context = {
        'category': category,
        'text_lexemes': text_lexemes,
        'subcategories': subcategories,
        'navigation': navigation,
    }
    return render(request, 'dictionary/category.html', context)


def text_lexeme(request, slug):
    lemma = get_object_or_404(TextLexeme, slug=slug, is_published=True)

    meaning_mappings = lemma.lexeme_meanings.select_related('meaning').order_by('-is_primary')
    meanings = [m.meaning for m in meaning_mappings]

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
        if words.exists():
            synonyms_by_meaning[meaning] = words

    gesture_lexemes = GestureLexeme.objects.filter(
        text_pairs__text_lexeme=lemma
    ).distinct()

    gesture_realizations = GestureRealization.objects.filter(
        gesture_lexeme__in=gesture_lexemes,
        moderation_status='approved'
    ).select_related('gesture_lexeme', 'author')

    main_gesture = gesture_realizations.filter(is_primary=True).first()
    other_gestures = gesture_realizations.exclude(
        id=main_gesture.id if main_gesture else None
    )

    in_personal = False
    if request.user.is_authenticated:
        in_personal = PersonalDictionary.objects.filter(
            user=request.user,
            text_lexeme=lemma
        ).exists()

    categories = lemma.categories.all()

    navigation = []
    if categories.exists():
        current = categories.first()
        path = []
        while current:
            path.insert(0, current)
            current = current.parent
        for cat in path[:-1]:
            navigation.append({'name': cat.name, 'href': reverse('category', kwargs={'slug': cat.slug})})

    context = {
        'lemma': lemma,
        'meaning_mappings': meaning_mappings,
        'meanings': meanings,
        'synonyms': synonyms,
        'synonyms_by_meaning': synonyms_by_meaning,
        'main_gesture': main_gesture,
        'other_gestures': other_gestures,
        'gesture_realizations': gesture_realizations,
        'categories': categories,
        'navigation': navigation,
        'in_personal': in_personal,
    }
    return render(request, 'dictionary/text_lexeme.html', context)

