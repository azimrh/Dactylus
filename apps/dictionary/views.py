from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from .forms import CustomUserCreationForm
from .models import (
    News, User,
    Category,
    TextLexeme, TextLexemeCompose,
    GestureLexeme, GestureLexemeCompose,
    GestureRealization, LexemePair
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


def home(request):
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
    return render(request, 'dictionary/home.html', context)


def dictionary(request):
    """Главная страница словаря — список корневых категорий."""
    categories = Category.objects.filter(
        parent=None
    ).prefetch_related('children').annotate(
        subcategories_count=Count('children', distinct=True),
        words_count=Count('textlexeme', filter=Q(textlexeme__is_published=True), distinct=True),
        gestures_count=Count('gesturelexeme', filter=Q(gesturelexeme__is_published=True), distinct=True),
    )

    return render(request, 'dictionary/dictionary.html', {
        'categories': categories,
        'category': None,
    })


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

    # Слова с пагинацией
    text_lexemes_list = TextLexeme.objects.filter(
        categories=category,
        is_published=True
    ).select_related('author').prefetch_related('meanings').order_by('text')

    paginator = Paginator(text_lexemes_list, 24)
    page = request.GET.get('page')
    text_lexemes = paginator.get_page(page)

    return render(request, 'dictionary/dictionary.html', {
        'category': category,
        'navigation': navigation,
        'subcategories': subcategories,
        'text_lexemes': text_lexemes
    })

# TODO

def add_category(request):
    return render(request, 'dictionary/add-category.html',)

def add_word(request):
    return render(request, 'dictionary/add-word.html',)

def text_lexeme(request, slug):
    lemma = get_object_or_404(
        TextLexeme.objects.prefetch_related('meanings', 'categories'),
        slug=slug,
        is_published=True
    )

    # Получаем связанные жесты через LexemePair
    lexeme_pairs = LexemePair.objects.filter(
        text_lexeme_type__model='textlexeme',
        text_lexeme_id=lemma.id
    )

    # Собираем ID жестов по типам
    gesture_ids_by_type = {}
    for pair in lexeme_pairs:
        type_id = pair.gesture_lexeme_type_id
        if type_id not in gesture_ids_by_type:
            gesture_ids_by_type[type_id] = []
        gesture_ids_by_type[type_id].append(pair.gesture_lexeme_id)

    # Загружаем жесты отдельно по типам
    gesture_lexemes = []
    for type_id, ids in gesture_ids_by_type.items():
        ct = ContentType.objects.get_for_id(type_id)
        model_class = ct.model_class()
        if model_class:
            gestures = model_class.objects.filter(id__in=ids)
            gesture_lexemes.extend(list(gestures))

    # Получаем ID всех жестов для поиска реализаций
    all_gesture_ids = [g.id for g in gesture_lexemes]

    # Реализации через GenericForeignKey — нельзя select_related на gesture_lexeme
    gesture_realizations = GestureRealization.objects.filter(
        lexeme_type__model__in=['gesturelexeme', 'gesturelexemecompose'],
        lexeme_id__in=all_gesture_ids,
        moderation_status='approved'
    ).select_related('author', 'moderated_by')

    # Группировка по жестам
    main_gesture = gesture_realizations.first()
    other_gestures = list(gesture_realizations.exclude(
        id=main_gesture.id if main_gesture else None
    ))

    meanings = list(lemma.meanings.all())
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
        if words:
            synonyms_by_meaning[meaning] = words

    # Навигация
    categories = lemma.categories.all()
    navigation = []
    if categories:
        current = categories.first()
        path = []
        while current:
            path.insert(0, current)
            current = current.parent
        for cat in path:
            navigation.append({
                'name': cat.name,
                'href': reverse('category', kwargs={'slug': cat.slug})
            })

    context = {
        'lemma': lemma,
        'meanings': meanings,
        'synonyms': synonyms,
        'synonyms_by_meaning': synonyms_by_meaning,
        'main_gesture': main_gesture,
        'other_gestures': other_gestures,
        'gesture_realizations': gesture_realizations,
        'gesture_lexemes': gesture_lexemes,
        'categories': categories,
        'navigation': navigation,
    }
    return render(request, 'dictionary/text_lexeme.html', context)

