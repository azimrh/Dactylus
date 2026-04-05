from django.contrib import admin

from .models import (
    Category,
    TextLexeme,  # TextLexemeCompose, TextComposeItem,
    GestureLexeme,  # GestureLexemeCompose, GestureComposeItem,
    LexemePair,
    GestureRealization,
    Meaning, LexemeMeaningMapping,
    Personal
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['parent']
    search_fields = ['name']


# -----------------------
# Значения и их связи с лексемами
# -----------------------

@admin.register(LexemeMeaningMapping)
class LexemeMeaningMappingAdmin(admin.ModelAdmin):
    list_display = ('lexeme', 'meaning', 'is_primary')
    list_filter = ('is_primary', 'lexeme_type')
    search_fields = ('meaning__description',)


@admin.register(Meaning)
class MeaningAdmin(admin.ModelAdmin):
    list_display = ('description', 'created_at')
    search_fields = ('description',)


# -----------------------
# Текстовые леммы
# -----------------------

@admin.register(TextLexeme)
class TextLexemeAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'is_letter', 'created_at', 'moderation_status')
    search_fields = ('text',)
    list_filter = ('is_letter', 'moderation_status', 'categories')

# -----------------------
# Жестовые леммы
# -----------------------

@admin.register(GestureLexeme)
class GestureLexemeAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'is_letter', 'created_at', 'moderation_status')
    search_fields = ('text',)
    list_filter = ('is_letter', 'moderation_status', 'categories')


@admin.register(GestureRealization)
class GestureRealizationAdmin(admin.ModelAdmin):
    list_display = ['gesture_lexeme', 'author', 'is_primary', 'moderation_status', 'created_at']
    list_filter = ['is_primary', 'moderation_status', 'created_at']
    search_fields = ['gesture_lexeme__text', 'author__username']
    readonly_fields = ['created_at']


# -----------------------
# Связи текст <-> жест
# -----------------------
@admin.register(LexemePair)
class LexemePairAdmin(admin.ModelAdmin):
    list_display = ('get_text_lexeme', 'get_gesture_lexeme', 'moderation_status', 'created_by', 'created_at')
    search_fields = ('text_lexeme__text', 'gesture_lexeme__text')
    list_filter = ['moderation_status']

    def get_text_lexeme(self, obj):
        return str(obj.page_text_lexeme) if obj.page_text_lexeme else '-'

    get_text_lexeme.short_description = 'Текстовая лемма'

    def get_gesture_lexeme(self, obj):
        return str(obj.gesture_lexeme) if obj.gesture_lexeme else '-'

    get_gesture_lexeme.short_description = 'Жестовая лемма'


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_item', 'status', 'added_at', 'last_reviewed')
    list_filter = ('status', 'content_type', 'added_at')
    search_fields = ('user__username', 'user__email', 'notes', 'object_id')
    date_hierarchy = 'added_at'
    readonly_fields = ('added_at', 'last_reviewed', 'content_object')

    fieldsets = (
        (None, {
            'fields': ('user', 'content_type', 'object_id')
        }),
        ('Элемент', {
            'fields': ('content_object',),
            'classes': ('collapse',)
        }),
        ('Статус изучения', {
            'fields': ('status', 'notes', 'last_reviewed')
        }),
        ('Даты', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )

    def get_item(self, obj):
        return str(obj.content_object) if obj.content_object else f"{obj.content_type.name} #{obj.object_id}"

    get_item.short_description = 'Элемент'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content_type', 'user')
