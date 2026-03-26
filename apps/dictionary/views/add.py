from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Max
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from slugify import slugify

from .base import group_required
from ..models import GestureRealization, GestureLexeme
from ..models.lexical import Category, TextLexeme, LexemePair
from ..utils.media_processing import process_image, video_to_gif, process_video


@login_required
@group_required('admin', 'linguist', 'moderator')
def add_category(request):
    parent_slug = request.GET.get('parent', '').strip() or request.POST.get('parent_slug', '').strip()

    parent = None
    if parent_slug:
        try:
            parent = Category.objects.get(slug=parent_slug)
        except ObjectDoesNotExist:
            messages.error(request, 'Родительская категория не найдена')
            return redirect('dictionary')

    if parent:
        sibling_categories = Category.objects.filter(parent=parent).order_by('order', 'name')
    else:
        sibling_categories = Category.objects.filter(parent__isnull=True).order_by('order', 'name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        order_value = request.POST.get('order', 'last')
        parent_slug = request.POST.get('parent_slug', None)
        image = request.FILES.get('image')

        errors = []
        if not name:
            errors.append('Введите название категории')
        if len(name) > 100:
            errors.append('Название не может быть длиннее 100 символов')

        # Проверка на существование категории
        cat = Category.objects.get(name=name)
        if cat:
            errors.append('Категория с таким именем уже существует!')

        parent = None
        if parent_slug:
            try:
                parent = Category.objects.get(slug=parent_slug)
            except Category.DoesNotExist:
                errors.append('Родительская категория не найдена')

        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}{counter}"
            counter += 1

        if errors:
            return render(request,
                'dictionary/add-category.html', {
                'errors': errors,
                'parent': parent,
                'sibling_categories': sibling_categories,
            })

        order = 0
        if order_value == 'first':
            Category.objects.filter(parent=parent).update(order=F('order') + 1)
            order = 0
        elif order_value == 'last':
            last_order = Category.objects.filter(parent=parent).aggregate(
                max_order=Max('order')
            )['max_order'] or -1
            order = last_order + 1
        elif order_value.startswith('after:'):
            try:
                after_slug = order_value.split(':', 1)[1]
                after_category = Category.objects.get(slug=after_slug, parent=parent)
                order = after_category.order + 1
                Category.objects.filter(
                    parent=parent,
                    order__gte=order
                ).update(order=F('order') + 1)
            except (Category.DoesNotExist, ValueError, IndexError):
                last_order = Category.objects.filter(parent=parent).aggregate(
                    max_order=Max('order')
                )['max_order'] or -1
                order = last_order + 1

        # Создание категории с parent!
        category = Category(
            name=name,
            slug=slug,
            parent=parent,
            order=order
        )

        if image:
            processed_image = process_image(image)
            if processed_image:
                category.image = processed_image

        category.save()
        messages.success(request, f'Категория "{name}" успешно создана.')
        return redirect('category', slug=category.slug)

    return render(request,
        'dictionary/add-category.html',
        {
            'parent': parent,
            'sibling_categories': sibling_categories,
        }
    )


@login_required
def add_word(request):
    if request.method == 'POST':
        word = request.POST.get('word', '').strip()
        video = request.FILES.get('video')
        user = request.user

        errors = []
        if not word:
            errors.append('Введите слово')
        if len(word) > 50:
            errors.append('Слово не может быть длиннее 50 символов')
        if not video:
            errors.append('Загрузите видео!')
        if errors:
            return render(request,
                'dictionary/add-word.html',
                {
                    "errors": errors
                }
            )

        # TextLexeme
        text_lexeme, created = TextLexeme.objects.get_or_create(
            text=word,
            defaults={
                'slug': slugify(word),
                'author': user,
                'is_published': True
            }
        )
        print(text_lexeme)

        # GestureLexeme
        gesture_lexeme, created = GestureLexeme.objects.get_or_create(
            text=word,
            defaults={
                'slug': text_lexeme.slug,
                'author': user,
                'is_published': True
            }
        )
        print(gesture_lexeme)

        # GestureRealization
        processed_video = process_video(video)
        gif = video_to_gif(processed_video)

        realization = GestureRealization.objects.create(
            lexeme_type=ContentType.objects.get_for_model(GestureLexeme),
            lexeme_id=gesture_lexeme.id,
            video=processed_video,
            gif=gif,
            author=user,
            is_primary=True,
            moderation_status='approved'
        )
        print(realization)

        # Связь через LexemePair
        LexemePair.objects.get_or_create(
            text_lexeme_type=ContentType.objects.get_for_model(TextLexeme),
            text_lexeme_id=text_lexeme.id,
            gesture_lexeme_type=ContentType.objects.get_for_model(GestureLexeme),
            gesture_lexeme_id=gesture_lexeme.id,
            defaults={'created_by': user}
        )

        messages.success(request, f'Слово "{word}" и жест успешно добавлены.')

    return render(request,
        'dictionary/add-word.html'
    )
