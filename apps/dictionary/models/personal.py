from django.db import models

from apps.users.models import User


class Personal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_items')
    lexeme_pair = models.ForeignKey('LexemePair', on_delete=models.CASCADE, null=True)  # Временно null=True

    status = models.CharField(max_length=20, choices=[
        ('new', 'Новое'),
        ('learning', 'Изучаю'),
        ('learned', 'Выучено')
    ], default='new')

    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lexeme_pair']
        ordering = ['-added_at']
