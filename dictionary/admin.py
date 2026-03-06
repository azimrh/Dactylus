from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'hearing_status', 'role', 'is_verified', 'rating', 'date_joined']
    list_filter = ['hearing_status', 'role', 'is_verified', 'is_staff', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('hearing_status', 'role', 'is_verified', 'region', 'bio', 'avatar', 'rating')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['parent']
    search_fields = ['name']


@admin.register(Meaning)
class MeaningAdmin(admin.ModelAdmin):
    list_display = ['description_short', 'hypernym', 'created_at']
    search_fields = ['description']
    autocomplete_fields = ['hypernym']

    def description_short(self, obj):
        return obj.description[:50]
    description_short.short_description = 'Описание'


class TextMeaningMappingInline(admin.TabularInline):
    model = TextMeaningMapping
    extra = 1
    autocomplete_fields = ['meaning']

class GestureMeaningMappingInline(admin.TabularInline):
    model = GestureMeaningMapping
    extra = 1
    autocomplete_fields = ['meaning']


@admin.register(TextLemma)
class TextLemmaAdmin(admin.ModelAdmin):
    list_display = ['text', 'is_published', 'is_dialectal', 'region']
    list_filter = ['is_published', 'is_dialectal', 'categories', 'created_at']
    search_fields = ['text', 'description']
    prepopulated_fields = {'slug': ('text',)}
    filter_horizontal = ['categories', 'related_lemmas', 'synonyms', 'antonyms']
    inlines = [TextMeaningMappingInline]

@admin.register(GestureLemma)
class GestureLemmaAdmin(admin.ModelAdmin):
    list_display = ['text', 'is_published', 'is_dialectal', 'region']
    list_filter = ['is_published', 'is_dialectal', 'created_at']
    search_fields = ['name', 'technical_description']
    filter_horizontal = ['related_lemmas', 'synonyms', 'antonyms']
    inlines = [GestureMeaningMappingInline]


@admin.register(TextMeaningMapping)
class TextMeaningMappingAdmin(admin.ModelAdmin):
    list_display = ['text_lemma', 'meaning', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['text_lemma__text', 'meaning__description']
    autocomplete_fields = ['text_lemma', 'meaning']

@admin.register(GestureMeaningMapping)
class GestureMeaningMappingAdmin(admin.ModelAdmin):
    list_display = ['gesture_lemma', 'meaning', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['gesture_lemma__name', 'meaning__description']
    autocomplete_fields = ['gesture_lemma', 'meaning']


@admin.register(GestureRealization)
class GestureRealizationAdmin(admin.ModelAdmin):
    list_display = ['gesture_lemma', 'author', 'is_primary', 'moderation_status', 'created_at']
    list_filter = ['is_primary', 'moderation_status', 'created_at']
    search_fields = ['gesture_lemma__name', 'author__username']
    autocomplete_fields = ['gesture_lemma', 'author', 'moderated_by']
    readonly_fields = ['created_at']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'published_at', 'author']
    list_filter = ['is_published', 'published_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)} if hasattr(News, 'slug') else {}
    autocomplete_fields = ['author']
