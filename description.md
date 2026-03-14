# Описание проекта

Словарь РЖЯ основан на формальном представлении языка в нескольких слоях.
В этой структуре слово и жест связаны через сущность ***ЗНАЧЕНИЕ*** (meaning), а также имеется отдельная абстракция для сочетаний слов и сочетаний жестов. Для видеозаписи жеста создаётся отдельная сущность реализации жеста.

## Лексический слой

Пользователь, участвующий в разметке словаря, участвует только в разметке лексического слоя, где создаются пары "текст" <-> "жест".

Пример:
```code
"привет" -> {привет}
"писатель" -> {автор} {человек} {книга}
"сценарист" -> {автор} {человек} {фильм}
"тоже" -> {тоже}
```

На примере "тоже" - создаётся не просто пара "тоже" -> {тоже}, а они связываются через смысл:
```code
"тоже" -> [тоже] <- {тоже}
```

Если встречается омоним - смысл дробится:
```
"тоже"    -> [тоже]  <- {тоже}
"похожий" -> [похож] <- {тоже}
```

То есть структура состоит из:
```code
1. TextLemma
2. GestureLemma
3. TextLemmaCompose
4. GestureLemmaCompose
5. Meaning

TextLemma           -> Meaning
TextLemmaCompose    -> Meaning
GestureLemma        -> Meaning
GestureLemmaCompose -> Meaning
```

Перевод слова/понятия  жесты происходит через смысл. Если их несколько - смысл уточняется:
```code
TLemma -> Meaning1
       -> Meaning2
       -> Meaning3 -> GLemma1
                   -> GLemma2
                   -> GLemma3
```

Такая структура работает в обе стороны, создавая лексический уровень.

## Связи
### Между леммами

* **Морфологические**
```code
Lemma -> Lemma
```
Пример:
```
"сценарий" -> "сценарист"
```

* **Стилистические**
```code
Lemma -> Lemma
Пример: "роза" -> "розочка"
```

### Связи между смыслами

* **Антонимия**
```code
Meaning <--> Meaning
```
Пример:
```
"Хорошо" <--> "плохо"
"свежий" <--> "давний"
```

* **Гиперонимия**
```code
Meaning -> Meaning
```
Пример:
```
[овчарка] -> [собака]
[собака] -> [животное]
```

* **Метонимия**
```code
Meaning -> Meaning
```
Пример:
```
[палец] -> [рука]
[страница] -> [книга]
```

## Поиск

Пользователь вводит поисковый запрос ***ТЕКСТОМ***.

Страница поиска делится на 2 колонки:
```code
|        ЗНАЧЕНИЯ      |  СЛОВА |
```

• ***ЗНАЧЕНИЯ*** - поиск по значениям, имеющим искомое слово, то что пользователю нужно в первую очередь
• ***СЛОВА*** - поиск по слову и похожим (морфологическими и стилистическими производными)

## Страница слова
Для слова "Работа"
```code
             Привет
|   Значения     |    Связи     |
|----------------_--------------|
|  1. Труд.      |  Морфолог.   |
| деятельность   | • рабочий    |
| • Труд         |  Стилистич.  |
| •              | • Работка    |
| •              | • Работёнка  |
|----------------_---------------
```

## Страница смысла
Для смысла "холодный / холод"
```code
|     Слова     |     Жесты     |
|---------------_---------------|
| Холодный      | |====| |====| |
| Прохладный    | |====| |====| |
| Морозный      |               |
| Холод         | |====| |====| |
| Мороз         | |====| |====| |
| Стужа         |               |
|---------------_---------------|

|             Связи             |
|-------------------------------|
|   Антонимические              |
| • В зн. физ. ощущ. - горячий, |
| теплый                        |
| • В зн. эмоций - теплый,      |
| радушный, сердечный           |
| • В зн. цвета - теплый        |
| • В зн. интеллект - горячий   |
|                               |
|   Гиперонимические            |
| Температурный признак ->      |
| -> Физическое свойство ->     |
| -> Свойство                   |
|                               |
|   Метонимические              |
| Лёд (следствие, проявление)   |
| Зима ()
| Снег (ассоциация)             |
| Мороз (с)
|-------------------------------|
```

# Код проекта

models/lexical.py
```python
from django.db import models
from django.urls import reverse

from .base import User


# Оставляем
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


# Готов
class TextLemma(models.Model):
    text = models.CharField(max_length=50, unique=True, verbose_name='Текстовая лемма')
    slug = models.SlugField(unique=True)
    categories = models.ManyToManyField(Category, related_name='text_lemmas', verbose_name='Категории')

    is_letter = models.BooleanField(default=False, verbose_name='Буква алфавита')
    letter_char = models.CharField(max_length=1, blank=True, verbose_name='Символ буквы')

    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_text_lemmas')
    created_at = models.DateTimeField(auto_now_add=True)

    meanings = models.ManyToManyField(
        'Meaning',
        through='TextMeaningMapping',
        related_name='text_lemmas',
        verbose_name='Смыслы'
    )

    class Meta:
        verbose_name = 'Текстовая лемма'
        verbose_name_plural = 'Текстовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('text_lemma', kwargs={'slug': self.slug})

class TextLemmaCompose(models.Model):
    text = models.CharField(max_length=200, verbose_name="Фраза")

    meanings = models.ManyToManyField(
        'Meaning',
        related_name='text_composes'
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    is_published = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Сочетание слов"

class TextComposeItem(models.Model):
    compose = models.ForeignKey(
        TextLemmaCompose,
        on_delete=models.CASCADE,
        related_name='items'
    )

    lemma = models.ForeignKey(TextLemma, on_delete=models.CASCADE)

    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']
        unique_together = ['compose', 'position']

        indexes = [
            models.Index(fields=['compose', 'position']),
            models.Index(fields=['lemma', 'position']),
        ]


class GestureLemma(models.Model):
    text = models.CharField(max_length=50, unique=True, verbose_name='Жестовая лемма')
    categories = models.ManyToManyField(Category, related_name='gesture_lemmas', verbose_name='Категории')

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

    class Meta:
        verbose_name = 'Жестовая лемма'
        verbose_name_plural = 'Жестовые леммы'
        ordering = ['text']

    def __str__(self):
        return self.text

class GestureLemmaCompose(models.Model):

    meanings = models.ManyToManyField(
        'Meaning',
        related_name='gesture_composes'
    )

    situation = models.CharField(max_length=100, blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    is_published = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Сочетание жестов"

class GestureComposeItem(models.Model):
    compose = models.ForeignKey(
        GestureLemmaCompose,
        on_delete=models.CASCADE,
        related_name='items'
    )

    lemma = models.ForeignKey(GestureLemma, on_delete=models.CASCADE)

    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']
        unique_together = ['compose', 'position']

        indexes = [
            models.Index(fields=['compose', 'position']),
            models.Index(fields=['lemma', 'position']),
        ]


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
```

models/lexical_pair.py
```python
from django.db import models
from .lexical import TextLemma, GestureLemma
from .semantic import Meaning
from .base import User


class LexemePair(models.Model):
    text_lemma = models.ForeignKey(
        TextLemma,
        on_delete=models.CASCADE,
        related_name='gesture_pairs'
    )

    gesture_lemma = models.ForeignKey(
        GestureLemma,
        on_delete=models.CASCADE,
        related_name='text_pairs'
    )

    meaning = models.ForeignKey(
        Meaning,
        on_delete=models.CASCADE,
        related_name='pairs'
    )

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    is_auto_meaning = models.BooleanField(
        default=True,
        help_text="Автоматически созданный смысл"
    )

    class Meta:
        verbose_name = 'Связь текст<-->жест'
        verbose_name_plural = 'Связи текст<-->жест'
        unique_together = ['text_lemma', 'gesture_lemma', 'meaning']
```

models/semantic.py
```python
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
```

Исправь модели, сделав леммы и их композиции равнозначными, чтобы они все имели категории и работали согласно описанной модели формализации.