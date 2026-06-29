from django.db import models
from apps.users.models import User


class Personal(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('learning', 'Изучаю'),
        ('learned', 'Выучено')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='personal_items'
    )
    lexeme_pair = models.ForeignKey(
        'dictionary.LexemePair',
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,  # ← использовать константу
        default='new'
    )
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lexeme_pair']
        ordering = ['-added_at']