from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from .news import User


class Meaning(models.Model):
    description = models.TextField(verbose_name='Описание значения', null=True)

    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На проверке'),
            ('approved', 'Одобрено'),
            ('rejected', 'Отклонено')
        ],
        default='pending'
    )

    personal_entries = GenericRelation('Personal', related_query_name='personal_meaning')

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Значение (денотат)'
        verbose_name_plural = 'Значение (денотаты)'
        app_label = 'dictionary'

    def __str__(self):
        return self.description[:50]


class LexemeMeaningMapping(models.Model):
    lexeme_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    lexeme_id = models.PositiveIntegerField()
    lexeme = GenericForeignKey('lexeme_type', 'lexeme_id')

    is_auto_meaning = models.BooleanField(default=True, verbose_name='Создано автоматически')

    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False, verbose_name='Основное значение')


    class Meta:
        unique_together = ['lexeme_type', 'lexeme_id', 'meaning']
        verbose_name = 'Связь лемма-значение'
        verbose_name_plural = 'Связи лемма-значение'
        app_label = 'dictionary'
        indexes = [
            models.Index(fields=['lexeme_type', 'lexeme_id']),
        ]