from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from .base import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Описание')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='Родительская категория')
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class TextLemma(models.Model):
    text = models.CharField(max_length=50, unique=True, verbose_name='Текстовая лемма')
    slug = models.SlugField(unique=True)
    categories = models.ManyToManyField(Category, related_name='text_lemmas', verbose_name='Категории')

    gestures = models.ManyToManyField(
        'GestureLemma',
        through='TextGestureMapping',
        related_name='mapped_texts',  # для доступа с GestureLemma
        related_query_name='gesture_text',  # для фильтров в queryset
        verbose_name='Жесты'
    )

    meanings = models.ManyToManyField(
        'Meaning',
        through='TextMeaningMapping',
        related_name='text_lemmas',
        verbose_name='Смыслы'
    )

    situation = models.CharField(max_length=100, blank=True, verbose_name='Ситуация использования')
    emotional_coloring = models.CharField(max_length=50, blank=True, verbose_name='Эмоциональная окраска')

    region = models.CharField(max_length=100, blank=True, verbose_name='Регион')
    is_dialectal = models.BooleanField(default=False, verbose_name='Диалектный')

    # Для букв
    is_letter = models.BooleanField(default=False, verbose_name='Буква алфавита')
    letter_char = models.CharField(max_length=1, blank=True, verbose_name='Символ буквы')

    # System
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_text_lemmas')
    created_at = models.DateTimeField(auto_now_add=True)

    # Relations
    synonyms = models.ManyToManyField('self', blank=True, symmetrical=True, through='TextSynonymRelation', verbose_name='Синонимы')
    antonyms = models.ManyToManyField('self', blank=True, symmetrical=False, through='TextAntonymRelation', related_name='antonyms_rel', verbose_name='Антонимы')
    related_lemmas = models.ManyToManyField('self', blank=True, symmetrical=True, verbose_name='Похожие слова')

    class Meta:
        verbose_name = 'Текстовая лемма'
        verbose_name_plural = 'Текстовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('text_lemma_detail', kwargs={'slug': self.slug})

class GestureLemma(models.Model):
    text = models.CharField(max_length=50, unique=True, verbose_name='Жестовая лемма')

    texts = models.ManyToManyField(
        'TextLemma',
        through='TextGestureMapping',
        related_name='mapped_gestures',  # для доступа с TextLemma
        related_query_name='gesture',  # для фильтров в queryset
        verbose_name='Слова'
    )

    meanings = models.ManyToManyField(
        'Meaning',
        through='GestureMeaningMapping',
        related_name='gesture_lemmas',
        verbose_name='Смыслы'
    )

    situation = models.CharField(max_length=100, blank=True, verbose_name='Ситуация использования')
    emotional_coloring = models.CharField(max_length=50, blank=True, verbose_name='Эмоциональная окраска')

    region = models.CharField(max_length=100, blank=True, verbose_name='Регион')
    is_dialectal = models.BooleanField(default=False, verbose_name='Диалектный')

    # Для букв
    is_letter = models.BooleanField(default=False, verbose_name='Жест буквы')
    letter_char = models.CharField(max_length=1, blank=True, verbose_name='Символ буквы')

    # System
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_gesture_lemmas')
    created_at = models.DateTimeField(auto_now_add=True)

    # Relations
    synonyms = models.ManyToManyField('self', blank=True, symmetrical=True, through='GestureSynonymRelation', verbose_name='Синонимы')
    antonyms = models.ManyToManyField('self', blank=True, symmetrical=False, through='GestureAntonymRelation', related_name='antonyms_rel', verbose_name='Антонимы')
    related_lemmas = models.ManyToManyField('self', blank=True, symmetrical=True, verbose_name='Похожие слова')


    class Meta:
        verbose_name = 'Жестовая лемма'
        verbose_name_plural = 'Жестовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

class TextGestureMapping(models.Model):
    text_lemma = models.ForeignKey(
        TextLemma,
        on_delete=models.CASCADE,
        related_name='gesture_mappings'
    )

    gesture_lemma = models.ForeignKey(
        GestureLemma,
        on_delete=models.CASCADE,
        related_name='text_mappings'
    )

    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['text_lemma', 'gesture_lemma']
        verbose_name = 'Связь слово-жест'
        verbose_name_plural = 'Связи слово-жест'

    def __str__(self):
        return f"{self.text_lemma.text} ↔ {self.gesture_lemma.text}"

class GestureRealization(models.Model):
    gesture_lemma = models.ForeignKey(GestureLemma, on_delete=models.CASCADE, related_name='realizations', verbose_name='Жестовая лемма')
    is_primary = models.BooleanField(default=False, verbose_name='Основная реализация')

    video = models.FileField(upload_to='videos/gestures/', verbose_name='Видео')
    image = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gesture_realizations')
    created_at = models.DateTimeField(auto_now_add=True)

    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На проверке'),
            ('approved', 'Одобрено'),
            ('rejected', 'Отклонено'),
        ],
        default='pending',
        verbose_name='Статус модерации'
    )
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_realizations')
    moderation_comment = models.TextField(blank=True, verbose_name='Комментарий модератора')

    class Meta:
        verbose_name = 'Реализация жеста (видео)'
        verbose_name_plural = 'Реализации жестов (видео)'
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.gesture_lemma.text} - {self.author.username}"

class TextSynonymRelation(models.Model):
    from_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='text_synonym_from')
    to_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='text_synonym_to')

    class Meta:
        unique_together = ['from_lemma', 'to_lemma']
        verbose_name = 'Текст. синонимическая связь'
        verbose_name_plural = 'Текст. синонимические связи'

class GestureSynonymRelation(models.Model):
    from_lemma = models.ForeignKey(GestureLemma, on_delete=models.CASCADE, related_name='gesture_synonym_from')
    to_lemma = models.ForeignKey(GestureLemma, on_delete=models.CASCADE, related_name='gesture_synonym_to')

    class Meta:
        unique_together = ['from_lemma', 'to_lemma']
        verbose_name = 'Жест. синонимическая связь'
        verbose_name_plural = 'Жест. синонимические связи'

class TextAntonymRelation(models.Model):
    from_lemma = models.ForeignKey(GestureLemma, on_delete=models.CASCADE, related_name='text_antonym_from')
    to_lemma = models.ForeignKey(GestureLemma, on_delete=models.CASCADE, related_name='text_antonym_to')

    class Meta:
        unique_together = ['from_lemma', 'to_lemma']
        verbose_name = 'Текст. антонимическая связь'
        verbose_name_plural = 'Текст. антонимические связи'

class GestureAntonymRelation(models.Model):
    from_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='gesture_antonym_from')
    to_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='gesture_antonym_to')

    class Meta:
        unique_together = ['from_lemma', 'to_lemma']
        verbose_name = 'Жест. антонимическая связь'
        verbose_name_plural = 'Жест. антонимические связи'
