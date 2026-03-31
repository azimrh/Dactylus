from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .news import User


class Personal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_items')

    # GFK на любую лексему или значение
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    status = models.CharField(max_length=20, choices=[
        ('new', 'Новое'),
        ('learning', 'Изучаю'),
        ('learned', 'Выучено')
    ], default='new')

    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'content_type', 'object_id']
        ordering = ['-added_at']
