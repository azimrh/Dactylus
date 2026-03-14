from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    HEARING_STATUS_CHOICES = [
        ('hearing', 'Слышащий'),
        ('hard_of_hearing', 'Слабослышащий'),
        ('deaf', 'Глухой'),
    ]

    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('native', 'Носитель РЖЯ'),
        ('linguist', 'Лингвист'),
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
