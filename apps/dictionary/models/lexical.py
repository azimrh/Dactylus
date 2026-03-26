from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from .news import User

# Допустимые модели для GenericForeignKey
ALLOWED_LEXEME_TYPES = {
    'textlexeme': 'Текстовая лемма',
    'textlexemecompose': 'Сочетание слов',
    'gesturelexeme': 'Жестовая лемма',
    'gesturelexemecompose': 'Сочетание жестов',
}


def get_allowed_content_types():
    """Возвращает ContentType IDs для разрешённых моделей."""
    return ContentType.objects.filter(
        model__in=list(ALLOWED_LEXEME_TYPES.keys())
    )


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Описание')

    parent = models.ForeignKey(
        'self',
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
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')

    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории'
    )

    meanings = models.ManyToManyField(
        'Meaning',
        related_name='%(class)s_set',
        verbose_name='Смыслы'
    )

    class Meta:
        abstract = True


class TextLexeme(BaseLexeme):
    text = models.CharField(max_length=200, verbose_name='Текст / Жест')
    slug = models.SlugField(unique=True)

    is_letter = models.BooleanField(default=False, verbose_name='Буква / Жест буквы')
    letter_char = models.CharField(max_length=1, blank=True, verbose_name='Символ буквы')

    pairs = GenericRelation(
        'LexemePair',
        content_type_field='text_lexeme_type',
        object_id_field='text_lexeme_id',
        related_query_name='text_lexeme'
    )

    class Meta:
        verbose_name = 'Текстовая лемма'
        verbose_name_plural = 'Текстовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('text_lexeme', kwargs={'slug': self.slug})

'''
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
    compose = models.ForeignKey(
        TextLexemeCompose,
        on_delete=models.CASCADE,
        related_name='compose_items'
    )
    text_lexeme = models.ForeignKey(TextLexeme, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']
        unique_together = ['compose', 'position']
        indexes = [
            models.Index(fields=['compose', 'position']),
            models.Index(fields=['text_lexeme', 'position']),
        ]
'''

class GestureLexeme(BaseLexeme):
    text = models.CharField(unique=True, max_length=200, verbose_name='Текст / Жест')
    slug = models.SlugField(unique=True)

    is_letter = models.BooleanField(default=False, verbose_name='Буква / Жест буквы')
    letter_char = models.CharField(max_length=1, blank=True, verbose_name='Символ буквы')

    pairs = GenericRelation(
        'LexemePair',
        content_type_field='gesture_lexeme_type',
        object_id_field='gesture_lexeme_id',
        related_query_name='gesture_pairs'
    )

    realizations = GenericRelation(
        'GestureRealization',
        content_type_field='lexeme_type',
        object_id_field='lexeme_id',
        related_query_name='gesture_realizations'
    )

    class Meta:
        verbose_name = 'Жестовая лемма'
        verbose_name_plural = 'Жестовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

'''
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
    compose = models.ForeignKey(
        GestureLexemeCompose,
        on_delete=models.CASCADE,
        related_name='compose_items'
    )
    gesture_lexeme = models.ForeignKey(GestureLexeme, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']
        unique_together = ['compose', 'position']
        indexes = [
            models.Index(fields=['compose', 'position']),
            models.Index(fields=['gesture_lexeme', 'position']),
        ]
'''

class LexemePair(models.Model):
    """Связь текстовой и жестовой леммы с ограничением типов."""

    # Текстовая лемма (только TextLexeme или TextLexemeCompose)
    text_lexeme_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='text_pairs',
        limit_choices_to={'model__in': ['textlexeme', 'textlexemecompose']}
    )
    text_lexeme_id = models.PositiveIntegerField()
    text_lexeme = GenericForeignKey('text_lexeme_type', 'text_lexeme_id')

    # Жестовая лемма (только GestureLexeme или GestureLexemeCompose)
    gesture_lexeme_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='gesture_pairs',
        limit_choices_to={'model__in': ['gesturelexeme', 'gesturelexemecompose']}
    )
    gesture_lexeme_id = models.PositiveIntegerField()
    gesture_lexeme = GenericForeignKey('gesture_lexeme_type', 'gesture_lexeme_id')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_auto_meaning = models.BooleanField(
        default=True,
        help_text="Автоматически созданный смысл"
    )

    class Meta:
        verbose_name = 'Связь текст<-->жест'
        verbose_name_plural = 'Связи текст<-->жест'
        indexes = [
            models.Index(fields=['text_lexeme_type', 'text_lexeme_id']),
            models.Index(fields=['gesture_lexeme_type', 'gesture_lexeme_id']),
        ]

    def clean(self):
        """Валидация типов лемм."""
        from django.core.exceptions import ValidationError

        text_model = self.text_lexeme_type.model
        gesture_model = self.gesture_lexeme_type.model

        allowed_text = ['textlexeme', 'textlexemecompose']
        allowed_gesture = ['gesturelexeme', 'gesturelexemecompose']

        if text_model not in allowed_text:
            raise ValidationError(
                f'Текстовая лемма должна быть одного из типов: {allowed_text}'
            )

        if gesture_model not in allowed_gesture:
            raise ValidationError(
                f'Жестовая лемма должна быть одного из типов: {allowed_gesture}'
            )


class GestureRealization(models.Model):
    """Реализация жеста с ограничением типа леммы."""

    lexeme_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ['gesturelexeme', 'gesturelexemecompose']}
    )
    lexeme_id = models.PositiveIntegerField()
    gesture_lexeme = GenericForeignKey('lexeme_type', 'lexeme_id')

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
        gesture = getattr(self, 'gesture_lexeme', None)
        return f"{getattr(gesture, 'text', 'Unknown gesture')} - {self.author.username}"

    def clean(self):
        """Валидация типа леммы."""
        from django.core.exceptions import ValidationError

        allowed = ['gesturelexeme', 'gesturelexemecompose']
        if self.lexeme_type.model not in allowed:
            raise ValidationError(
                f'Лемма должна быть жестовой: {allowed}'
            )