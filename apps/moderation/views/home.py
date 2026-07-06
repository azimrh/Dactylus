from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from apps.dictionary.models import (
    Meaning,
    TextLexeme, GestureLexeme,
    LexemeTriplet, GestureRealization
)
from apps.dictionary.views._base import group_required


@login_required
@group_required('moderator')
def moderation_home(request):
    """Главная страница модерации с данными для всех вкладок"""

    # Статистика по текстовым леммам
    text_pending = TextLexeme.objects.filter(moderation_status='pending').count()
    text_approved = TextLexeme.objects.filter(moderation_status='approved').count()
    text_rejected = TextLexeme.objects.filter(moderation_status='rejected').count()

    # Статистика по жестовым леммам
    gesture_pending = GestureLexeme.objects.filter(moderation_status='pending').count()
    gesture_approved = GestureLexeme.objects.filter(moderation_status='approved').count()
    gesture_rejected = GestureLexeme.objects.filter(moderation_status='rejected').count()

    # Статистика по смыслам
    meaning_pending = Meaning.objects.filter(moderation_status='pending').count()
    meaning_approved = Meaning.objects.filter(moderation_status='approved').count()
    meaning_rejected = Meaning.objects.filter(moderation_status='rejected').count()

    # Статистика по триплетам (вместо пар)
    triplet_pending = LexemeTriplet.objects.filter(moderation_status='pending').count()
    triplet_approved = LexemeTriplet.objects.filter(moderation_status='approved').count()
    triplet_rejected = LexemeTriplet.objects.filter(moderation_status='rejected').count()

    # Статистика по видео
    video_pending = GestureRealization.objects.filter(moderation_status='pending').count()
    video_approved = GestureRealization.objects.filter(moderation_status='approved').count()
    video_rejected = GestureRealization.objects.filter(moderation_status='rejected').count()

    pending_words = TextLexeme.objects.filter(
        moderation_status='pending'
    ).select_related('author').order_by('-created_at')[:20]

    pending_gestures = GestureLexeme.objects.filter(
        moderation_status='pending'
    ).select_related('author').prefetch_related('realizations').order_by('-created_at')[:20]

    pending_meanings = Meaning.objects.filter(
        moderation_status='pending'
    ).select_related('author').order_by('-created_at')[:20]

    pending_triplets = LexemeTriplet.objects.filter(
        moderation_status='pending'
    ).select_related(
        'text_lexeme',
        'gesture_lexeme',
        'meaning',
        'created_by'
    ).prefetch_related(
        'categories',
        'gesture_lexeme__realizations'
    ).order_by('-created_at')

    paginator = Paginator(pending_triplets, 20)
    page_number = request.GET.get('page')
    pending_triplets_page = paginator.get_page(page_number)

    # Данные для вкладки "Видео"
    pending_videos = GestureRealization.objects.filter(
        moderation_status='pending'
    ).select_related(
        'gesture_lexeme',
        'author'
    ).order_by('-created_at')[:20]

    context = {
        # Статистика
        'text_pending': text_pending,
        'text_approved': text_approved,
        'text_rejected': text_rejected,

        'meaning_pending': meaning_pending,
        'meaning_approved': meaning_approved,
        'meaning_rejected': meaning_rejected,

        'triplet_pending': triplet_pending,
        'triplet_approved': triplet_approved,
        'triplet_rejected': triplet_rejected,

        'video_pending': video_pending,
        'video_approved': video_approved,
        'video_rejected': video_rejected,

        # Данные для вкладок
        'pending_words': pending_words,
        'pending_gestures': pending_gestures,
        'pending_meanings': pending_meanings,
        'pending_triplets': pending_triplets_page,
        'pending_videos': pending_videos,
    }

    return render(request, 'moderation/home.html', context)