from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .base import User


class Meaning(models.Model):
    description = models.TextField(verbose_name='Описание смысла', null=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Смысл (денотат)'
        verbose_name_plural = 'Смыслы (денотаты)'
        app_label = 'dictionary'  # Добавляю явное указание приложения

    def __str__(self):
        return self.description[:50]


class LexemeMeaningMapping(models.Model):
    lexeme_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    lexeme_id = models.PositiveIntegerField()
    lexeme = GenericForeignKey('lexeme_type', 'lexeme_id')

    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False, verbose_name='Основное значение')

    class Meta:
        unique_together = ['lexeme_type', 'lexeme_id', 'meaning']
        verbose_name = 'Связь лемма-смысл'
        verbose_name_plural = 'Связи лемма-смысл'
        app_label = 'dictionary'  # Добавляю явное указание приложения
        indexes = [
            models.Index(fields=['lexeme_type', 'lexeme_id']),
        ]