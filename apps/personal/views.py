import json
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from apps.personal.models import Personal
from apps.dictionary.models import LexemeTriplet, GestureRealization


@login_required
def page_personal(request):
    user = request.user

    # Получаем элементы личного словаря
    entries = Personal.objects.filter(user=user).select_related(
        'lexeme_triplet__text_lexeme',
        'lexeme_triplet__gesture_lexeme'
    ).order_by('-added_at')

    text_entries = []

    # Для оптимизации собираем ID жестов, чтобы получить их реализации (видео/gif) одним запросом
    gesture_ids = [e.lexeme_triplet.gesture_lexeme_id for e in entries if e.lexeme_triplet.gesture_lexeme_id]
    realizations_map = {}

    if gesture_ids:
        # Берем только первичные реализации для превью
        realizations = GestureRealization.objects.filter(
            gesture_lexeme_id__in=gesture_ids,
            is_primary=True,
            moderation_status='approved'
        )
        for r in realizations:
            if r.gesture_lexeme_id not in realizations_map:
                realizations_map[r.gesture_lexeme_id] = r

    for entry in entries:
        triplet = entry.lexeme_triplet
        if triplet and triplet.text_lexeme:
            text_lexeme = triplet.text_lexeme

            # Добавляем данные из личного словаря прямо к объекту лексемы для шаблона
            text_lexeme.personal_status = entry.status
            text_lexeme.personal_notes = entry.notes
            text_lexeme.personal_entry_id = entry.id
            text_lexeme.triplet_id = triplet.id

            # Добавляем информацию о жесте и его реализации
            text_lexeme.gesture_lexeme = triplet.gesture_lexeme

            # Находим реализацию (gif/video)
            realization = realizations_map.get(triplet.gesture_lexeme_id)
            if realization:
                text_lexeme.primary_image = realization.gif_mini.url if realization.gif_mini else (
                    realization.gif.url if realization.gif else None)
            else:
                text_lexeme.primary_image = None

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
    return render(request, 'personal/home.html', context)


class PersonalAddView(LoginRequiredMixin, View):
    """Добавление триплета в личный словарь (AJAX)."""

    def post(self, request):
        # Изменено: принимаем lexeme_triplet_id вместо lexeme_pair_id
        triplet_id = request.POST.get('lexeme_triplet_id')

        if not triplet_id:
            return JsonResponse(
                {'error': 'Missing lexeme_triplet_id parameter'},
                status=400
            )

        try:
            triplet = LexemeTriplet.objects.get(
                id=triplet_id,
                moderation_status='approved'
            )
        except LexemeTriplet.DoesNotExist:
            return JsonResponse(
                {'error': 'Triplet not found or not approved'},
                status=404
            )

        existing = Personal.objects.filter(
            user=request.user,
            lexeme_triplet=triplet
        ).first()

        if existing:
            return JsonResponse({
                'success': True,
                'created': False,
                'id': existing.id,
                'status': existing.status,
                'message': 'Already in personal dictionary'
            })

        entry = Personal.objects.create(
            user=request.user,
            lexeme_triplet=triplet,
            status='new',
            last_reviewed=timezone.now()
        )

        return JsonResponse({
            'success': True,
            'created': True,
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
        valid_statuses = dict(Personal.STATUS_CHOICES)

        if status not in valid_statuses:
            return JsonResponse(
                {'error': f'Invalid status. Valid: {list(valid_statuses.keys())}'},
                status=400
            )

        entry.status = status
        entry.last_reviewed = timezone.now()
        entry.save()

        return JsonResponse({
            'success': True,
            'status': entry.status,
            'last_reviewed': entry.last_reviewed.isoformat()
        })