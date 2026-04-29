from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""
    username = models.TextField(max_length=30, unique=True)
    email = models.EmailField(unique=True)

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    HEARING_STATUS_CHOICES = [
        ('hearing', 'Слышащий'),
        ('hard', 'Слабослышащий'),
        ('deaf', 'Глухой'),
    ]

    hearing_status = models.CharField(
        max_length=20,
        choices=HEARING_STATUS_CHOICES,
        default='hearing',
        verbose_name='Статус слуха',
        db_index=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
