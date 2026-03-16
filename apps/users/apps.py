from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'
    verbose_name = 'Пользователи'

    def ready(self):
        from . import signals
        from django.db.models.signals import post_migrate

        post_migrate.connect(signals.create_system_groups, sender=self)
