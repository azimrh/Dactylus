import json
from datetime import timezone

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType

from ..models import Personal, TextLexeme, GestureLexeme, Meaning, LexemePair


@login_required
def page_personal(request):
    user = request.user

    entries = Personal.objects.filter(user=user).select_related(
        'lexeme_pair__text_lexeme',
        'lexeme_pair__gesture_lexeme'
    ).prefetch_related(
        'lexeme_pair__text_lexeme__meanings',
        'lexeme_pair__gesture_lexeme__realizations'
    )

    text_entries = []
    for entry in entries:
        pair = entry.lexeme_pair
        if pair and pair.text_lexeme:
            text_lexeme = pair.text_lexeme
            text_lexeme.personal_status = entry.status
            text_lexeme.personal_notes = entry.notes
            text_lexeme.personal_entry_id = entry.id
            text_lexeme.gesture_lexeme = pair.gesture_lexeme
            text_entries.append(text_lexeme)

    stats = {
        'words': {
            'total': entries.count(),
            'learned': entries.filter(status='learned').count(),
            'learning': entries.filter(status='learning').count(),
        }
    }

    context = {
        'text_entries': text_entries,
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
    def delete(self, request, entry_id):
        entry = get_object_or_404(Personal, id=entry_id, user=request.user)
        entry.delete()
        return JsonResponse({'success': True})


class PersonalUpdateStatusView(LoginRequiredMixin, View):
    def patch(self, request, entry_id):
        entry = get_object_or_404(Personal, id=entry_id, user=request.user)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        status = data.get('status')
        if status not in dict(Personal.STATUS_CHOICES):
            return JsonResponse({'error': 'Invalid status'}, status=400)

        entry.status = status
        if status == 'learned':
            entry.last_reviewed = timezone.now()
        entry.save()

        return JsonResponse({
            'success': True,
            'status': entry.status
        })