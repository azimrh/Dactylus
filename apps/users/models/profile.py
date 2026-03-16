from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, verbose_name='О себе')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'users'
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class UserStats(models.Model):
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='stats'
    )
    signs_added = models.PositiveIntegerField(default=0)
    signs_verified = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'users'
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'
