from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from apps.dictionary.models import Category, TextLexeme, LexemeTriplet, GestureRealization
from apps.personal.models import Personal


def page_text_lexeme(request, slug):
    lemma = get_object_or_404(TextLexeme, slug=slug)

    # Получаем все триплеты для этого слова
    triplets = LexemeTriplet.objects.filter(
        text_lexeme=lemma,
        moderation_status='approved'
    ).select_related('meaning', 'gesture_lexeme')

    # Группировка по значению для отображения синонимов и вариантов
    meanings_data = {}
    gesture_realizations = []

    for t in triplets:
        if t.meaning not in meanings_data:
            meanings_data[t.meaning] = []
        meanings_data[t.meaning].append(t)

    # Собираем реализации жестов из всех триплетов
    gesture_ids = [t.gesture_lexeme_id for t in triplets]
    if gesture_ids:
        gesture_realizations = GestureRealization.objects.filter(
            gesture_lexeme_id__in=gesture_ids,
            moderation_status='approved'
        ).select_related('author', 'gesture_lexeme')

    main_gesture = gesture_realizations.first()

    # Категории (берем из первого попавшегося триплета или объединяем)
    categories = Category.objects.filter(
        lexemetriplet__text_lexeme=lemma,
        lexemetriplet__moderation_status='approved'
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

    # Для личного словаря берем первый триплет
    first_triplet = triplets.first()
    triplet_id = first_triplet.id if first_triplet else None

    in_personal = False
    if request.user.is_authenticated and triplet_id:
        # Предполагаем, что Personal теперь ссылается на LexemeTriplet
        # или нужно адаптировать модель Personal.
        # Здесь показана проверка по старой логике, но поле должно быть lexeme_triplet_id
        in_personal = Personal.objects.filter(
            user=request.user,
            lexeme_triplet_id=triplet_id
        ).exists()

    return render(request, 'dictionary/text_lexeme.html', {
        'lemma': lemma,
        'meanings_data': meanings_data,  # Словарь {Meaning: [Triplets]}
        'main_gesture': main_gesture,
        'gesture_realizations': gesture_realizations,
        'categories': categories,
        'navigation': navigation,
        'triplet_id': triplet_id,
        'in_personal': in_personal,
    })