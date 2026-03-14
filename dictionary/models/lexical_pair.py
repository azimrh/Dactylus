from django.db import models
from .lexical import TextLemma, GestureLemma
from .semantic import Meaning
from .base import User


class LexemePair(models.Model):
    text_lemma = models.ForeignKey(
        TextLemma,
        on_delete=models.CASCADE,
        related_name='gesture_pairs'
    )

    gesture_lemma = models.ForeignKey(
        GestureLemma,
        on_delete=models.CASCADE,
        related_name='text_pairs'
    )

    meaning = models.ForeignKey(
        Meaning,
        on_delete=models.CASCADE,
        related_name='pairs'
    )

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    is_auto_meaning = models.BooleanField(
        default=True,
        help_text="Автоматически созданный смысл"
    )

    class Meta:
        verbose_name = 'Связь текст<-->жест'
        verbose_name_plural = 'Связи текст<-->жест'
        unique_together = ['text_lemma', 'gesture_lemma', 'meaning']
