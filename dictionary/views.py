from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm
from .models import (
    News, User,
    Category, TextLemma, GestureLemma, GestureRealization,
    PersonalDictionary
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

    # Статистика
    stats = {
        'gestures': GestureLemma.objects.filter(is_published=True).count(),
        'words': TextLemma.objects.filter(is_published=True).count(),
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

    context = {
        'categories': categories
    }
    return render(request, 'dictionary/dictionary.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # Построение хлебных крошек
    navigation = []
    current = category
    while current.parent:
        navigation.insert(0, {
            'name': current.parent.name,
            'href': reverse('category_detail', kwargs={'slug': current.parent.slug})
        })
        current = current.parent

    # Слова с привязанными жестами
    text_lemmas = TextLemma.objects.filter(
        categories=category,
        is_published=True
    ).prefetch_related('meanings')

    # Подкатегории
    subcategories = category.children.all()

    context = {
        'category': category,
        'text_lemmas': text_lemmas,
        'subcategories': subcategories,
        'navigation': navigation,  # для хлебных крошек
    }
    return render(request, 'dictionary/category_detail.html', context)


def text_lemma_detail(request, slug):
    lemma = get_object_or_404(TextLemma, slug=slug, is_published=True)

    # Получаем связанные смыслы с приоритетом
    meaning_mappings = lemma.textmeaningmapping_set.select_related('meaning').order_by('-is_primary')

    # Синонимы и антонимы
    synonyms = lemma.synonyms.filter(is_published=True)
    antonyms = lemma.antonyms.filter(is_published=True)
    related = lemma.related_lemmas.filter(is_published=True)

    # Проверка в личном словаре
    in_personal = False
    if request.user.is_authenticated:
        in_personal = PersonalDictionary.objects.filter(
            user=request.user,
            text_lemma=lemma
        ).exists()

    context = {
        'lemma': lemma,
        'meaning_mappings': meaning_mappings,
        'synonyms': synonyms,
        'antonyms': antonyms,
        'related_lemmas': related,
        'in_personal': in_personal,
    }
    return render(request, 'dictionary/word_detail.html', context)


def gesture_lemma_detail(request, pk):
    lemma = get_object_or_404(GestureLemma, pk=pk, is_published=True)

    # Получаем связанные смыслы
    meaning_mappings = lemma.gesturemeaningmapping_set.select_related('meaning').order_by('-is_primary', '-usage_preference_score')

    # Синонимы и антонимы (жестовые)
    synonyms = lemma.synonyms.filter(is_published=True)
    antonyms = lemma.antonyms.filter(is_published=True)
    related = lemma.related_lemmas.filter(is_published=True)

    # Проверка в личном словаре
    in_personal = False
    if request.user.is_authenticated:
        in_personal = PersonalDictionary.objects.filter(
            user=request.user,
            gesture_lemma=lemma
        ).exists()

    context = {
        'lemma': lemma,
        'is_gesture': True,
        'meaning_mappings': meaning_mappings,
        'synonyms': synonyms,
        'antonyms': antonyms,
        'related_lemmas': related,
        'in_personal': in_personal,
    }
    return render(request, 'dictionary/word_detail.html', context)


@login_required
def personal_dict(request):
    entries = PersonalDictionary.objects.filter(
        user=request.user
    ).select_related('text_lemma', 'gesture_lemma', 'meaning')

    stats = {
        'total': entries.count(),
        'learned': entries.filter(proficiency__gte=4).count(),
        'learning': entries.filter(proficiency__gte=1, proficiency__lt=4).count(),
    }

    context = {
        'entries': entries,
        'stats': stats,
    }
    return render(request, 'dictionary/personal_dict.html', context)


@login_required
@require_POST
def add_to_personal(request, lemma_type, lemma_id):
    """
    lemma_type: 'text' или 'gesture'
    """
    if lemma_type == 'text':
        lemma = get_object_or_404(TextLemma, id=lemma_id)
        entry, created = PersonalDictionary.objects.get_or_create(
            user=request.user,
            text_lemma=lemma,
            defaults={'proficiency': 0}
        )
    elif lemma_type == 'gesture':
        lemma = get_object_or_404(GestureLemma, id=lemma_id)
        entry, created = PersonalDictionary.objects.get_or_create(
            user=request.user,
            gesture_lemma=lemma,
            defaults={'proficiency': 0}
        )
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid lemma type'}, status=400)

    return JsonResponse({'status': 'added' if created else 'exists'})


@login_required
def contribute(request):
    return redirect('home')
    return render(request, 'dictionary/contribute.html')


@login_required
def annotation(request):
    return redirect('home')
    return render(request, 'dictionary/annotation.html')


@login_required
def moderation(request):
    if not request.user.role in ['moderator', 'admin'] and not request.user.is_superuser:
        return redirect('home')

    # Модерация текстовых и жестовых лемм
    pending_text_lemmas = TextLemma.objects.filter(is_published=False)
    pending_gesture_lemmas = GestureLemma.objects.filter(is_published=False)

    context = {
        'pending_text_lemmas': pending_text_lemmas,
        'pending_gesture_lemmas': pending_gesture_lemmas,
    }
    return render(request, 'dictionary/moderation.html', context)
