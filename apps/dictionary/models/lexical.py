from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from .news import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Описание')

    parent = models.ForeignKey('self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская категория'
    )
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})


class BaseLexeme(models.Model):
    text = models.CharField(max_length=200, verbose_name='Текст / Жест')
    slug = models.SlugField(unique=True)

    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На проверке'),
            ('approved', 'Одобрено'),
            ('rejected', 'Отклонено')
        ],
        default='pending'
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории'
    )

    meanings = models.ManyToManyField(
        'Meaning',
        related_name='%(class)s_set',
        verbose_name='Значения'
    )

    class Meta:
        abstract = True


class TextLexeme(BaseLexeme):
    is_letter = models.BooleanField(default=False, verbose_name='Буква / Жест буквы')
    letter_char = models.CharField(max_length=1, blank=True, verbose_name='Символ буквы')

    personal_entries = GenericRelation('Personal', related_query_name='personal_text_lexeme')

    class Meta:
        verbose_name = 'Текстовая лемма'
        verbose_name_plural = 'Текстовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('text_lexeme', kwargs={'slug': self.slug})


class GestureLexeme(BaseLexeme):
    is_letter = models.BooleanField(default=False, verbose_name='Буква / Жест буквы')
    letter_char = models.CharField(max_length=1, blank=True, verbose_name='Символ буквы')

    personal_entries = GenericRelation('Personal', related_query_name='personal_gesture_lexeme')

    class Meta:
        verbose_name = 'Жестовая лемма'
        verbose_name_plural = 'Жестовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('text_lexeme', kwargs={'slug': self.slug})


class LexemePair(models.Model):
    """Связь текстовой и жестовой леммы."""

    text_lexeme = models.ForeignKey(
        TextLexeme,
        on_delete=models.CASCADE,
        related_name='pairs',
        verbose_name='Текстовая лемма'
    )

    gesture_lexeme = models.ForeignKey(
        GestureLexeme,
        on_delete=models.CASCADE,
        related_name='pairs',
        verbose_name='Жестовая лемма'
    )

    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На проверке'),
            ('approved', 'Одобрено'),
            ('rejected', 'Отклонено')
        ],
        default='pending'
    )

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Связь текст<-->жест'
        verbose_name_plural = 'Связи текст<-->жест'
        unique_together = ['text_lexeme', 'gesture_lexeme']
        indexes = [
            models.Index(fields=['text_lexeme']),
            models.Index(fields=['gesture_lexeme']),
        ]


class GestureRealization(models.Model):
    """Реализация жеста."""

    gesture_lexeme = models.ForeignKey(
        GestureLexeme,
        on_delete=models.CASCADE,
        related_name='realizations',
        verbose_name='Жестовая лемма'
    )

    video = models.FileField(upload_to='videos/gestures/')
    gif = models.FileField(upload_to='gif/gestures/')
    image = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На проверке'),
            ('approved', 'Одобрено'),
            ('rejected', 'Отклонено')
        ],
        default='pending'
    )
    moderated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='moderated_realizations'
    )
    moderation_comment = models.TextField(blank=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_realizations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Реализация жеста'
        verbose_name_plural = 'Реализации жестов'

    def __str__(self):
        return f"{self.gesture_lexeme.text} - {self.author.username}"
