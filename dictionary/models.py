from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    HEARING_STATUS_CHOICES = [
        ('hearing', 'Слышащий'),
        ('hard_of_hearing', 'Слабослышащий'),
        ('deaf', 'Глухой'),
    ]

    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('native', 'Носитель РЖЯ'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    hearing_status = models.CharField(
        max_length=20,
        choices=HEARING_STATUS_CHOICES,
        default='hearing',
        verbose_name='Статус слуха'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
    )
    is_verified = models.BooleanField(default=False, verbose_name='Верифицирован')
    region = models.CharField(max_length=100, blank=True, verbose_name='Регион')
    bio = models.TextField(blank=True, verbose_name='О себе')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.username} ({self.get_hearing_status_display()})"

    def is_native_speaker(self):
        return self.hearing_status == 'deaf' or self.role == 'native'


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Описание')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children', verbose_name='Родительская категория')
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Meaning(models.Model):
    """
    Смысл (денотат) - абстрактное понятие, не зависящее от языка.
    """
    description = models.TextField(verbose_name='Описание смысла')
    hypernym = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='hyponyms', verbose_name='Верхнее понятие')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Смысл (денотат)'
        verbose_name_plural = 'Смыслы (денотаты)'

    def __str__(self):
        return self.description[:50]


class TextLemma(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Текстовая лемма')
    slug = models.SlugField(unique=True)
    categories = models.ManyToManyField(Category, related_name='text_lemmas', verbose_name='Категории')

    meanings = models.ManyToManyField(
        Meaning,
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
    synonyms = models.ManyToManyField('self', blank=True, symmetrical=True, through='SynonymRelation', verbose_name='Синонимы')
    antonyms = models.ManyToManyField('self', blank=True, symmetrical=False, through='AntonymRelation', related_name='antonyms_rel', verbose_name='Антонимы')
    related_lemmas = models.ManyToManyField('self', blank=True, symmetrical=True, verbose_name='Похожие слова')

    class Meta:
        verbose_name = 'Текстовая лемма'
        verbose_name_plural = 'Текстовые леммы'
        ordering = ['name']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('text_lemma_detail', kwargs={'slug': self.slug})


class GestureLemma(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Жестовая лемма')

    meanings = models.ManyToManyField(
        Meaning,
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
    synonyms = models.ManyToManyField('self', blank=True, symmetrical=True, through='SynonymRelation', verbose_name='Синонимы')
    antonyms = models.ManyToManyField('self', blank=True, symmetrical=False, through='AntonymRelation', related_name='antonyms_rel', verbose_name='Антонимы')
    related_lemmas = models.ManyToManyField('self', blank=True, symmetrical=True, verbose_name='Похожие слова')


    class Meta:
        verbose_name = 'Жестовая лемма'
        verbose_name_plural = 'Жестовые леммы'
        ordering = ['name']

    def __str__(self):
        return self.name


class TextMeaningMapping(models.Model):
    text_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE)
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False, verbose_name='Основное значение')

    usage_preference_score = models.FloatField(default=1.0, verbose_name='Предпочтение использования')

    class Meta:
        unique_together = ['text_lemma', 'meaning']
        verbose_name = 'Связь текст-смысл'
        verbose_name_plural = 'Связи текст-смысл'


class GestureMeaningMapping(models.Model):
    gesture_lemma = models.ForeignKey(GestureLemma, on_delete=models.CASCADE)
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False, verbose_name='Основное значение')

    usage_preference_score = models.FloatField(default=1.0, verbose_name='Предпочтение использования')

    class Meta:
        unique_together = ['gesture_lemma', 'meaning']
        verbose_name = 'Связь жест-смысл'
        verbose_name_plural = 'Связи жест-смысл'


class SynonymRelation(models.Model):
    from_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='synonym_from')
    to_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='synonym_to')

    class Meta:
        unique_together = ['from_lemma', 'to_lemma']
        verbose_name = 'Синонимическая связь'
        verbose_name_plural = 'Синонимические связи'


class AntonymRelation(models.Model):
    from_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='antonym_from')
    to_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='antonym_to')

    class Meta:
        unique_together = ['from_lemma', 'to_lemma']
        verbose_name = 'Антонимическая связь'
        verbose_name_plural = 'Антонимические связи'


class TextExplanation(models.Model):
    """
    Последовательность текстовых лемм - объяснение смысла текстом.
    """
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE, related_name='text_explanations')
    sequence = models.JSONField(verbose_name='Последовательность лемм (ID)')
    raw_text = models.TextField(verbose_name='Текстовое представление')
    is_primary = models.BooleanField(default=False, verbose_name='Основное объяснение')

    # System
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='text_explanations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Текстовое объяснение'
        verbose_name_plural = 'Текстовые объяснения'


class GestureExplanation(models.Model):
    """
    Последовательность жестовых лемм - объяснение смысла жестами.
    """
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE, related_name='gesture_explanations')
    sequence = models.JSONField(verbose_name='Последовательность жестов (ID)')
    is_primary = models.BooleanField(default=False, verbose_name='Основное объяснение')

    # System
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gesture_explanations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Жестовое объяснение'
        verbose_name_plural = 'Жестовые объяснения'


class TextExample(models.Model):
    """
    Пример фразы текстом - последовательность текстовых лемм.
    """
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE, related_name='text_examples')
    sequence = models.JSONField(verbose_name='Последовательность лемм (ID)')
    raw_text = models.TextField(verbose_name='Текстовое представление')
    situation = models.CharField(max_length=100, blank=True, verbose_name='Ситуация использования')  # ДОБАВЛЕНО

    # System
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='text_examples')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Текстовый пример'
        verbose_name_plural = 'Текстовые примеры'


class GestureExample(models.Model):
    """
    Пример фразы жестами - последовательность жестовых лемм.
    """
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE, related_name='gesture_examples')
    sequence = models.JSONField(verbose_name='Последовательность жестов (ID)')
    situation = models.CharField(max_length=100, blank=True, verbose_name='Ситуация использования')  # ДОБАВЛЕНО

    # System
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gesture_examples')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Жестовый пример'
        verbose_name_plural = 'Жестовые примеры'

'''
class GestureRealization(models.Model):
    """
    Конкретная видео-реализация жестовой леммы.
    Это физическое воплощение абстрактной жестовой леммы.
    """
    gesture_lemma = models.ForeignKey(GestureLemma, on_delete=models.CASCADE,
                                      related_name='realizations', verbose_name='Жестовая лемма')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gesture_realizations')
    video = models.FileField(upload_to='videos/gestures/', verbose_name='Видео')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    # Технические характеристики исполнения
    execution_notes = models.TextField(blank=True, verbose_name='Особенности исполнения')

    is_primary = models.BooleanField(default=False, verbose_name='Основная реализация')
    views_count = models.IntegerField(default=0, verbose_name='Просмотры')
    created_at = models.DateTimeField(auto_now_add=True)

    # Модерация
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
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='moderated_realizations')
    moderation_comment = models.TextField(blank=True, verbose_name='Комментарий модератора')

    class Meta:
        verbose_name = 'Реализация жеста (видео)'
        verbose_name_plural = 'Реализации жестов (видео)'
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.gesture_lemma.code} - {self.author.username}"


class VideoAnnotation(models.Model):
    """
    Разметка видео-реализации для обучения ИИ.
    """
    realization = models.ForeignKey(GestureRealization, on_delete=models.CASCADE,
                                    related_name='annotations', verbose_name='Реализация')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_annotations')
    frame_number = models.IntegerField(verbose_name='Номер кадра')
    body_part = models.CharField(max_length=50, verbose_name='Часть тела')
    x_coordinate = models.FloatField(verbose_name='Координата X')
    y_coordinate = models.FloatField(verbose_name='Координата Y')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Разметка видео'
        verbose_name_plural = 'Разметки видео'

    def __str__(self):
        return f"Разметка {self.realization} - кадр {self.frame_number}"
'''

# ==================== МЕТОДЫ РАЗМЕТКИ ====================

class InvariantEvaluation(models.Model):
    ANSWER_CHOICES = [
        ('yes', 'Да, смысл сохранится'),
        ('context', 'Зависит от контекста'),
        ('no', 'Нет, смысл изменится'),
    ]

    # Исходная фраза как последовательность лемм
    phrase_sequence = models.JSONField(verbose_name='Последовательность лемм')
    phrase_text = models.TextField(verbose_name='Текст фразы')

    # Целевое слово и его замена
    target_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='invariant_evaluations_target')
    replacement_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='invariant_evaluations_replacement')

    # Контекст ситуации
    situation = models.CharField(max_length=100, blank=True, verbose_name='Ситуация')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invariant_evaluations')
    answer = models.CharField(max_length=20, choices=ANSWER_CHOICES, verbose_name='Ответ')

    # Если зависит от контекста - уточнение
    context_notes = models.TextField(blank=True, verbose_name='Уточнение контекста')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Оценка инварианта'
        verbose_name_plural = 'Оценки инвариантов'

    def __str__(self):
        return f"{self.target_lemma.text} → {self.replacement_lemma.text}: {self.get_answer_display()}"


class HomonymDisambiguation(models.Model):
    """
    Разметка контекста омонимов: примеры фраз для конкретного смысла.
    """
    text_lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE, related_name='disambiguations', verbose_name='Омоним')
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE, related_name='disambiguation_examples', verbose_name='Конкретный смысл')

    # Пример фразы как последовательность
    example_sequence = models.JSONField(verbose_name='Последовательность лемм примера')
    example_text = models.TextField(verbose_name='Текст примера')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='homonym_disambiguations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Разграничение омонима'
        verbose_name_plural = 'Разграничения омонимов'
        unique_together = ['text_lemma', 'meaning', 'user']

    def __str__(self):
        return f"{self.text_lemma.text} = {self.meaning.description[:30]}"

'''
class DialectalVote(models.Model):
    """
    Голосование за диалектизмы: выбор предпочитаемого варианта.
    """
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE, related_name='dialectal_votes')

    # Варианты жестов для одного смысла
    gesture_variant_1 = models.ForeignKey(GestureLemma, on_delete=models.CASCADE,
                                          related_name='dialectal_votes_1')
    gesture_variant_2 = models.ForeignKey(GestureLemma, on_delete=models.CASCADE,
                                          related_name='dialectal_votes_2', null=True, blank=True)

    # Выбор пользователя
    preferred_gesture = models.ForeignKey(GestureLemma, on_delete=models.CASCADE,
                                          related_name='preferred_in_votes')

    # Частота использования (всегда/часто/иногда/редко)
    usage_frequency = models.CharField(
        max_length=20,
        choices=[
            ('always', 'Всегда использую этот вариант'),
            ('often', 'Часто'),
            ('sometimes', 'Иногда'),
            ('rarely', 'Редко'),
        ],
        default='always',
        verbose_name='Частота использования'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dialectal_votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Голос за диалектизм'
        verbose_name_plural = 'Голоса за диалектизмы'
        unique_together = ['meaning', 'user']

    def __str__(self):
        return f"{self.user.username} предпочитает {self.preferred_gesture.code}"
'''

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
        lemma = self.text_lemma.name if self.text_lemma else self.gesture_lemma.name
        return f"{self.user.username} - {lemma}"


class TranslationCache(models.Model):
    """
    Кэш перевода текст -> жесты.
    """
    text_input = models.TextField(verbose_name='Входной текст')

    # Результат как последовательность жестовых лемм
    gesture_sequence = models.JSONField(verbose_name='Последовательность жестов')

    # Альтернативные варианты (синонимы)
    alternative_sequences = models.JSONField(default=list, verbose_name='Альтернативные варианты')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translation_caches', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_personalized = models.BooleanField(default=False, verbose_name='Персонализированный')

    class Meta:
        verbose_name = 'Кэш перевода'
        verbose_name_plural = 'Кэш переводов'

    def __str__(self):
        return f"Перевод: {self.text_input[:50]}..."


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    published_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title