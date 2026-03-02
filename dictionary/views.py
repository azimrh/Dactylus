from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm
from .models import (
    Category, Meaning, TextLemma, GestureLemma,
    TextExplanation, GestureExplanation,
    TextExample, GestureExample,
    PersonalDictionary, InvariantEvaluation,
    HomonymDisambiguation, News, User
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
    context = {
        'categories': categories,
        'news': news,
    }
    return render(request, 'dictionary/home.html', context)


def dictionary(request):
    categories = Category.objects.filter(parent=None).prefetch_related('children')
    search_query = request.GET.get('q', '')

    text_lemmas = None
    if search_query:
        text_lemmas = TextLemma.objects.filter(
            Q(name__icontains=search_query) |
            Q(situation__icontains=search_query) |
            Q(emotional_coloring__icontains=search_query),
            is_published=True
        ).prefetch_related('meanings', 'categories')

    context = {
        'categories': categories,
        'text_lemmas': text_lemmas,
        'search_query': search_query,
    }
    return render(request, 'dictionary/dictionary.html', context)


def text_lemma_detail(request, slug):
    lemma = get_object_or_404(TextLemma, slug=slug, is_published=True)

    # Получаем связанные смыслы с приоритетом
    meaning_mappings = lemma.textmeaningmapping_set.select_related('meaning').order_by('-is_primary', '-usage_preference_score')

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


def translator(request):
    return redirect('home')
    return render(request, 'dictionary/translator.html')


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


def contribute(request):
    return redirect('home')
    return render(request, 'dictionary/contribute.html')


@login_required
def invariants(request):
    return redirect('home')
    # Получаем случайную пару для оценки инварианта
    # Ищем пары синонимов, которые пользователь еще не оценивал
    evaluation = InvariantEvaluation.objects.exclude(
        user=request.user
    ).select_related('target_lemma', 'replacement_lemma').first()

    context = {
        'evaluation': evaluation,
        'progress': InvariantEvaluation.objects.filter(user=request.user).count(),
    }
    return render(request, 'dictionary/invariants.html', context)


@login_required
@require_POST
def submit_invariant(request):
    return redirect('home')
    target_id = request.POST.get('target_lemma_id')
    replacement_id = request.POST.get('replacement_lemma_id')
    answer = request.POST.get('answer')
    phrase_sequence = request.POST.get('phrase_sequence', '[]')
    phrase_text = request.POST.get('phrase_text', '')
    situation = request.POST.get('situation', '')
    context_notes = request.POST.get('context_notes', '')

    target_lemma = get_object_or_404(TextLemma, id=target_id)
    replacement_lemma = get_object_or_404(TextLemma, id=replacement_id)

    InvariantEvaluation.objects.create(
        user=request.user,
        target_lemma=target_lemma,
        replacement_lemma=replacement_lemma,
        answer=answer,
        phrase_sequence=phrase_sequence,
        phrase_text=phrase_text,
        situation=situation,
        context_notes=context_notes
    )

    return JsonResponse({'status': 'success'})


@login_required
def homonym_disambiguation(request):
    return redirect('home')
    # Получаем омонимы (леммы с несколькими смыслами), которые нужно разметить
    ambiguous_lemmas = TextLemma.objects.annotate(
        meaning_count=Count('meanings')
    ).filter(meaning_count__gt=1).exclude(
        disambiguations__user=request.user
    ).first()

    context = {
        'ambiguous_lemma': ambiguous_lemmas,
        'progress': HomonymDisambiguation.objects.filter(user=request.user).count(),
    }
    return render(request, 'dictionary/homonym_disambiguation.html', context)


@login_required
@require_POST
def submit_disambiguation(request):
    return redirect('home')
    text_lemma_id = request.POST.get('text_lemma_id')
    meaning_id = request.POST.get('meaning_id')
    example_sequence = request.POST.get('example_sequence', '[]')
    example_text = request.POST.get('example_text', '')

    text_lemma = get_object_or_404(TextLemma, id=text_lemma_id)
    meaning = get_object_or_404(Meaning, id=meaning_id)

    HomonymDisambiguation.objects.create(
        user=request.user,
        text_lemma=text_lemma,
        meaning=meaning,
        example_sequence=example_sequence,
        example_text=example_text
    )

    return JsonResponse({'status': 'success'})


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


@login_required
@require_POST
def moderate_lemma(request, lemma_type, lemma_id, action):
    return redirect('home')
    if not request.user.role in ['moderator', 'admin']:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)

    if lemma_type == 'text':
        lemma = get_object_or_404(TextLemma, id=lemma_id)
    elif lemma_type == 'gesture':
        lemma = get_object_or_404(GestureLemma, id=lemma_id)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid lemma type'}, status=400)

    if action == 'approve':
        lemma.is_published = True
        lemma.save()
        return JsonResponse({'status': 'approved'})
    elif action == 'reject':
        lemma.delete()
        return JsonResponse({'status': 'rejected'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # Текстовые леммы в категории
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
    }
    return render(request, 'dictionary/category_detail.html', context)


@login_required
def meaning_detail(request, pk):
    return redirect('home')
    """
    Детальная страница смысла (денотата) со всеми связанными леммами,
    объяснениями и примерами.
    """
    meaning = get_object_or_404(Meaning, pk=pk)

    # Все текстовые и жестовые леммы для этого смысла
    text_mappings = meaning.textmeaningmapping_set.select_related('text_lemma').order_by('-usage_preference_score')
    gesture_mappings = meaning.gesturemeaningmapping_set.select_related('gesture_lemma').order_by(
        '-usage_preference_score')

    # Объяснения и примеры
    text_explanations = meaning.text_explanations.select_related('author')
    gesture_explanations = meaning.gesture_explanations.select_related('author')
    text_examples = meaning.text_examples.select_related('author')
    gesture_examples = meaning.gesture_examples.select_related('author')

    # Иерархия: гиперонимы и гипонимы
    hypernym = meaning.hypernym
    hyponyms = meaning.hyponyms.all()

    context = {
        'meaning': meaning,
        'text_mappings': text_mappings,
        'gesture_mappings': gesture_mappings,
        'text_explanations': text_explanations,
        'gesture_explanations': gesture_explanations,
        'text_examples': text_examples,
        'gesture_examples': gesture_examples,
        'hypernym': hypernym,
        'hyponyms': hyponyms,
    }
    return render(request, 'dictionary/meaning_detail.html', context)


@login_required
@require_POST
def add_explanation(request):
    return redirect('home')
    """
    Добавление объяснения смысла (текстового или жестового).
    """
    meaning_id = request.POST.get('meaning_id')
    explanation_type = request.POST.get('type')  # 'text' или 'gesture'
    sequence = request.POST.get('sequence', '[]')
    raw_text = request.POST.get('raw_text', '')

    meaning = get_object_or_404(Meaning, id=meaning_id)

    if explanation_type == 'text':
        TextExplanation.objects.create(
            meaning=meaning,
            sequence=sequence,
            raw_text=raw_text,
            author=request.user
        )
    elif explanation_type == 'gesture':
        GestureExplanation.objects.create(
            meaning=meaning,
            sequence=sequence,
            author=request.user
        )
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid type'}, status=400)

    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def add_example(request):
    return redirect('home')
    """
    Добавление примера использования (текстового или жестового).
    """
    meaning_id = request.POST.get('meaning_id')
    example_type = request.POST.get('type')  # 'text' или 'gesture'
    sequence = request.POST.get('sequence', '[]')
    raw_text = request.POST.get('raw_text', '')
    situation = request.POST.get('situation', '')

    meaning = get_object_or_404(Meaning, id=meaning_id)

    if example_type == 'text':
        TextExample.objects.create(
            meaning=meaning,
            sequence=sequence,
            raw_text=raw_text,
            situation=situation,
            author=request.user
        )
    elif example_type == 'gesture':
        GestureExample.objects.create(
            meaning=meaning,
            sequence=sequence,
            situation=situation,
            author=request.user
        )
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid type'}, status=400)

    return JsonResponse({'status': 'success'})
