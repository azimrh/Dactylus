from django.db import models

from .base import User
from .lexical import TextLemma, GestureLemma
from .semantic import Meaning


class PersonalDictionary(models.Model):
    """
    Личный словарь пользователя - изучаемые леммы (текстовые и жестовые).
    """
    PROFICIENCY_LEVELS = [
        (0, 'Не изучено'),
        (1, 'Начинаю изучать'),
        (2, 'Знаю плохо'),
        (3, 'Знаю хорошо'),
        (4, 'Отлично знаю'),
        (5, 'Владею в совершенстве'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_dictionary')
    text_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, null=True, blank=True, related_name='in_personal_dicts')
    gesture_lemma = models.ForeignKey(GestureLemma, on_delete=models.CASCADE, null=True, blank=True, related_name='in_personal_dicts')

    # Привязка к конкретному смыслу (важно для омонимов!)
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE, null=True, blank=True, related_name='personal_dictionary_entries')

    proficiency = models.IntegerField(choices=PROFICIENCY_LEVELS, default=0, verbose_name='Уровень знания')
    practice_count = models.IntegerField(default=0, verbose_name='Количество тренировок')
    last_practiced = models.DateTimeField(null=True, blank=True, verbose_name='Последняя тренировка')
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name='Заметки')

    class Meta:
        verbose_name = 'Запись в личном словаре'
        verbose_name_plural = 'Личный словарь'
        unique_together = ['user', 'text_lemma', 'gesture_lemma', 'meaning']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(text_lemma__isnull=False) | models.Q(gesture_lemma__isnull=False),
                name='at_least_one_lemma'
            ),
        ]

    def __str__(self):
        lemma = self.text_lemma.text if self.text_lemma else self.gesture_lemma.text
        return f"{self.user.username} - {lemma}"
