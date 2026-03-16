from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

from .models import User, UserProfile, UserStats

SYSTEM_GROUPS = ['user', 'native', 'linguist', 'moderator', 'admin']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создаём профиль и добавляем в группу 'user' при регистрации."""
    if created:
        UserProfile.objects.create(user=instance)
        UserStats.objects.create(user=instance)

        # Добавляем в базовую группу
        group, _ = Group.objects.get_or_create(name='user')
        instance.groups.add(group)


def create_system_groups(sender, **kwargs):
    """Создаёт системные группы после миграции."""
    if sender.label != 'users':
        return

    for name in SYSTEM_GROUPS:
        Group.objects.get_or_create(name=name)
    print(f"✓ Созданы группы: {', '.join(SYSTEM_GROUPS)}")
