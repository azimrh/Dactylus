from django.db import models


class Meaning(models.Model):
    description = models.TextField(verbose_name='Описание смысла', null=True)
    hypernym = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='hyponyms', verbose_name='Верхнее понятие')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Смысл (денотат)'
        verbose_name_plural = 'Смыслы (денотаты)'

    def __str__(self):
        return self.description[:50]

class TextMeaningMapping(models.Model):
    text_lemma = models.ForeignKey('TextLemma', on_delete=models.CASCADE)
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False, verbose_name='Основное значение')

    class Meta:
        unique_together = ['text_lemma', 'meaning']
        verbose_name = 'Связь текст-смысл'
        verbose_name_plural = 'Связи текст-смысл'

class GestureMeaningMapping(models.Model):
    gesture_lemma = models.ForeignKey('GestureLemma', on_delete=models.CASCADE)
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False, verbose_name='Основное значение')

    class Meta:
        unique_together = ['gesture_lemma', 'meaning']
        verbose_name = 'Связь жест-смысл'
        verbose_name_plural = 'Связи жест-смысл'
