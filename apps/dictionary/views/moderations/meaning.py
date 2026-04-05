from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from apps.dictionary.models import Meaning
from ..base import group_required


@login_required
@group_required('moderator')
def moderation_meaning(request, pk):
    """Модерация смысла"""
    meaning = get_object_or_404(Meaning, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            new_description = request.POST.get('description', '').strip()

            if new_description:
                meaning.description = new_description

            meaning.moderation_status = 'approved'
            meaning.save()  # <-- всегда сохраняем статус

            messages.success(request, 'Смысл одобрен')
            return redirect('moderation')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            meaning.delete()
            messages.success(request, f'Смысл отклонен: {reason}')
            return redirect('moderation')

    return render(request, 'dictionary/moderation/meaning.html', {
        'meaning': meaning,
    })
