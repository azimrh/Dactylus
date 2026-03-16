from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .news import User


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
        return reverse('category', kwargs={'slug': self.slug})


class BaseLexeme(models.Model):
    text = models.CharField(max_length=200, verbose_name='Текст / Жест')
    categories = models.ManyToManyField(Category, verbose_name='Категории')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')

    meanings = models.ManyToManyField(
        'Meaning',
        related_name='%(class)s_set',
        verbose_name='Смыслы'
    )

    class Meta:
        abstract = True


class TextLexeme(BaseLexeme):
    slug = models.SlugField(unique=True)

    is_letter = models.BooleanField(default=False, verbose_name='Буква / Жест буквы')
    letter_char = models.CharField(max_length=1, blank=True, verbose_name='Символ буквы')

    class Meta:
        verbose_name = 'Текстовая лемма'
        verbose_name_plural = 'Текстовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('text_lexeme', kwargs={'slug': self.slug})

class TextLexemeCompose(BaseLexeme):
    items = models.ManyToManyField(
        TextLexeme,
        through='TextComposeItem',
        related_name='used_in_composes'
    )

    class Meta:
        verbose_name = "Сочетание слов"
        verbose_name_plural = "Сочетания слов"
        ordering = ['text']

class TextComposeItem(models.Model):
    compose = models.ForeignKey(TextLexemeCompose, on_delete=models.CASCADE, related_name='compose_items')
    text_lexeme = models.ForeignKey(TextLexeme, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']
        unique_together = ['compose', 'position']
        indexes = [
            models.Index(fields=['compose', 'position']),
            models.Index(fields=['text_lexeme', 'position']),
        ]


class GestureLexeme(BaseLexeme):
    video = models.FileField(upload_to='videos/gestures/', blank=True, null=True)
    image = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    is_letter = models.BooleanField(default=False, verbose_name='Буква / Жест буквы')
    letter_char = models.CharField(max_length=1, blank=True, verbose_name='Символ буквы')

    class Meta:
        verbose_name = 'Жестовая лемма'
        verbose_name_plural = 'Жестовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

class GestureLexemeCompose(BaseLexeme):
    items = models.ManyToManyField(
        GestureLexeme,
        through='GestureComposeItem',
        related_name='compose_set'
    )

    class Meta:
        verbose_name = "Сочетание жестов"
        verbose_name_plural = "Сочетания жестов"
        ordering = ['text']

class GestureComposeItem(models.Model):
    compose = models.ForeignKey(GestureLexemeCompose, on_delete=models.CASCADE, related_name='compose_items')
    gesture_lexeme = models.ForeignKey(GestureLexeme, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']
        unique_together = ['compose', 'position']
        indexes = [
            models.Index(fields=['compose', 'position']),
            models.Index(fields=['gesture_lexeme', 'position']),
        ]


class LexemePair(models.Model):
    text_lexeme_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='text_pairs'  # Оставляю как есть
    )
    text_lexeme_id = models.PositiveIntegerField()
    text_lexeme = GenericForeignKey('text_lexeme_type', 'text_lexeme_id')

    gesture_lexeme_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='gesture_pairs'  # Исправляю: было 'text_pairs', должно быть 'gesture_pairs'
    )
    gesture_lexeme_id = models.PositiveIntegerField()
    gesture_lexeme = GenericForeignKey('gesture_lexeme_type', 'gesture_lexeme_id')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_auto_meaning = models.BooleanField(default=True, help_text="Автоматически созданный смысл")

    class Meta:
        verbose_name = 'Связь текст<-->жест'
        verbose_name_plural = 'Связи текст<-->жест'
        indexes = [
            models.Index(fields=['text_lexeme_type', 'text_lexeme_id']),
            models.Index(fields=['gesture_lexeme_type', 'gesture_lexeme_id']),
        ]


class GestureRealization(models.Model):
    lexeme_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    lexeme_id = models.PositiveIntegerField()
    gesture_lexeme = GenericForeignKey('lexeme_type', 'lexeme_id')

    video = models.FileField(upload_to='videos/gestures/')
    image = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending','На проверке'),
            ('approved','Одобрено'),
            ('rejected','Отклонено')
        ],
        default='pending'
    )
    moderated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='moderated_realizations')
    moderation_comment = models.TextField(blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_realizations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Реализация жеста'
        verbose_name_plural = 'Реализации жестов'

    def __str__(self):
        return f"{self.gesture_lexeme.text} - {self.author.username}"
