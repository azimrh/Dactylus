from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType

from ..models import Personal, TextLexeme, GestureLexeme, Meaning, LexemePair


@login_required
def personal(request):
    """Основная страница личного словаря."""
    user = request.user

    # Получаем записи с префетчем связанных объектов
    entries = Personal.objects.filter(user=user).select_related('content_type')

    # Разделяем по типам контента
    text_ids = entries.filter(content_type__model='textlexeme').values_list('object_id', flat=True)
    gesture_ids = entries.filter(content_type__model='gesturelexeme').values_list('object_id', flat=True)
    meaning_ids = entries.filter(content_type__model='meaning').values_list('object_id', flat=True)
    pair_ids = entries.filter(content_type__model='lexemepair').values_list('object_id', flat=True)

    # Загружаем сами объекты
    text_entries = TextLexeme.objects.filter(id__in=text_ids).prefetch_related('meanings')
    gesture_entries = GestureLexeme.objects.filter(id__in=gesture_ids).prefetch_related('realizations')
    meaning_entries = Meaning.objects.filter(id__in=meaning_ids)
    pair_entries = LexemePair.objects.filter(id__in=pair_ids).select_related('text_lexeme', 'gesture_lexeme')

    # Статистика по статусам для каждого типа
    stats = {
        'words': {
            'total': len(text_ids),
            'learned': entries.filter(content_type__model='textlexeme', status='learned').count(),
            'learning': entries.filter(content_type__model='textlexeme', status='learning').count(),
        },
        'gestures': {
            'total': len(gesture_ids),
            'learned': entries.filter(content_type__model='gesturelexeme', status='learned').count(),
            'learning': entries.filter(content_type__model='gesturelexeme', status='learning').count(),
        },
        'meanings': {
            'total': len(meaning_ids),
            'learned': entries.filter(content_type__model='meaning', status='learned').count(),
            'learning': entries.filter(content_type__model='meaning', status='learning').count(),
        },
        'pairs': {
            'total': len(pair_ids),
            'learned': entries.filter(content_type__model='lexemepair', status='learned').count(),
            'learning': entries.filter(content_type__model='lexemepair', status='learning').count(),
        }
    }

    # Обогащаем объекты статусами из Personal
    def enrich_with_status(objs, model_name):
        status_map = {
            obj_id: status for obj_id, status in
            entries.filter(content_type__model=model_name).values_list('object_id', 'status')
        }
        notes_map = {
            obj_id: notes for obj_id, notes in
            entries.filter(content_type__model=model_name).values_list('object_id', 'notes')
        }
        for obj in objs:
            obj.personal_status = status_map.get(obj.id, 'new')
            obj.personal_notes = notes_map.get(obj.id, '')
        return objs

    text_entries = enrich_with_status(text_entries, 'textlexeme')
    gesture_entries = enrich_with_status(gesture_entries, 'gesturelexeme')
    meaning_entries = enrich_with_status(meaning_entries, 'meaning')
    pair_entries = enrich_with_status(pair_entries, 'lexemepair')

    context = {
        'text_entries': text_entries,
        'gesture_entries': gesture_entries,
        'meaning_entries': meaning_entries,
        'pair_entries': pair_entries,
        'stats': stats,
    }

    return render(request, 'dictionary/personal.html', context)


class PersonalAddView(LoginRequiredMixin, View):
    """Добавление элемента в личный словарь (AJAX)."""

    def post(self, request):
        content_type_id = request.POST.get('content_type')
        object_id = request.POST.get('object_id')

        if not content_type_id or not object_id:
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        try:
            ct = ContentType.objects.get(id=content_type_id)
            # Проверяем существование объекта
            obj = ct.model_class().objects.get(id=object_id)
        except (ContentType.DoesNotExist, AttributeError):
            return JsonResponse({'error': 'Invalid content type'}, status=400)
        except ct.model_class().DoesNotExist:
            return JsonResponse({'error': 'Object not found'}, status=404)

        # Создаем или получаем существующую запись
        entry, created = Personal.objects.get_or_create(
            user=request.user,
            content_type=ct,
            object_id=object_id,
            defaults={'status': 'new'}
        )

        return JsonResponse({
            'success': True,
            'created': created,
            'id': entry.id,
            'status': entry.status
        })


class PersonalRemoveView(LoginRequiredMixin, View):
    """Удаление элемента из личного словаря (AJAX)."""

    def post(self, request, entry_id):
        entry = get_object_or_404(Personal, id=entry_id, user=request.user)
        entry.delete()
        return JsonResponse({'success': True})


class PersonalUpdateStatusView(LoginRequiredMixin, View):
    """Обновление статуса изучения (AJAX)."""

    def post(self, request, entry_id):
        entry = get_object_or_404(Personal, id=entry_id, user=request.user)
        status = request.POST.get('status')

        if status not in dict(Personal.STATUS_CHOICES):
            return JsonResponse({'error': 'Invalid status'}, status=400)

        entry.status = status
        if status == 'learned':
            from django.utils import timezone
            entry.last_reviewed = timezone.now()
        entry.save()

        return JsonResponse({
            'success': True,
            'status': entry.status
        })


class PersonalUpdateNotesView(LoginRequiredMixin, View):
    """Обновление заметок (AJAX)."""

    def post(self, request, entry_id):
        entry = get_object_or_404(Personal, id=entry_id, user=request.user)
        notes = request.POST.get('notes', '')

        entry.notes = notes
        entry.save()

        return JsonResponse({'success': True})
