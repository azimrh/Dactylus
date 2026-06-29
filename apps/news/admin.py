from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at')
    list_filter = ('is_published', 'author')
    search_fields = ('title', 'content')
    readonly_fields = ('published_at',)