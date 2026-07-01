import json
from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone  # ← правильный импорт

from apps.personal.models import Personal
from apps.dictionary.models import LexemePair


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
    return render(request, 'personal/home.html', context)


class PersonalAddView(LoginRequiredMixin, View):
    """Добавление пары лексем в личный словарь (AJAX)."""

    def post(self, request):
        lexeme_pair_id = request.POST.get('lexeme_pair_id')

        if not lexeme_pair_id:
            return JsonResponse(
                {'error': 'Missing lexeme_pair_id parameter'},
                status=400
            )

        try:
            lexeme_pair = LexemePair.objects.get(
                id=lexeme_pair_id,
                moderation_status='approved'  # ← только одобренные пары
            )
        except LexemePair.DoesNotExist:
            return JsonResponse(
                {'error': 'Lexeme pair not found or not approved'},
                status=404
            )

        existing = Personal.objects.filter(
            user=request.user,
            lexeme_pair=lexeme_pair
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
            lexeme_pair=lexeme_pair,
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
        valid_statuses = dict(Personal.STATUS_CHOICES) if hasattr(Personal, 'STATUS_CHOICES') else {
            'new': 'Новое',
            'learning': 'Изучаю',
            'learned': 'Выучено'
        }

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