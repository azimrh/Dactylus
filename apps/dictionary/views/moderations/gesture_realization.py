from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from apps.dictionary.models import GestureRealization
from ..base import group_required


@login_required
@group_required('moderator')
def moderation_gesture_realization(request, pk):
    """Модерация видео (GestureRealization)"""
    video = get_object_or_404(GestureRealization, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            video.moderation_status = 'approved'
            video.moderated_by = request.user
            video.save()
            messages.success(request, f'Видео для "{video.gesture_lexeme.text}" одобрено')
            return redirect('moderation')

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            video.moderation_status = 'rejected'
            video.moderated_by = request.user
            video.moderation_comment = reason
            video.save()
            messages.success(request, f'Видео отклонено: {reason}')
            return redirect('moderation')

    return render(request, 'dictionary/moderation/video.html', {
        'video': video,
    })
