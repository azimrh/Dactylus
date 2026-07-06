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
    # Изменено: ссылка на триплет вместо пары
    lexeme_triplet = models.ForeignKey(
        'dictionary.LexemeTriplet',
        on_delete=models.CASCADE,
        related_name='personal_entries'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lexeme_triplet']
        ordering = ['-added_at']
        verbose_name = 'Элемент личного словаря'
        verbose_name_plural = 'Личный словарь'

    def __str__(self):
        return f"{self.user.username} - {self.lexeme_triplet.text_lexeme}"