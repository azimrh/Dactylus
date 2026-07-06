from django.contrib import admin
from .models import (
    Category, TextLexeme, GestureLexeme, LexemeTriplet,
    GestureRealization, Meaning
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['parent']
    search_fields = ['name']

@admin.register(Meaning)
class MeaningAdmin(admin.ModelAdmin):
    list_display = ('description', 'author', 'moderation_status', 'created_at')
    search_fields = ('description',)
    list_filter = ('moderation_status',)

@admin.register(TextLexeme)
class TextLexemeAdmin(admin.ModelAdmin):
    list_display = ('text', 'slug', 'author', 'is_letter', 'moderation_status', 'created_at')
    search_fields = ('text',)
    list_filter = ('is_letter', 'moderation_status')
    prepopulated_fields = {'slug': ('text',)}

@admin.register(GestureLexeme)
class GestureLexemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'is_letter', 'moderation_status', 'created_at')
    list_filter = ('is_letter', 'moderation_status')
    # Поиск по ID автора или другим полям, так как текста нет
    search_fields = ('author__username',)

@admin.register(LexemeTriplet)
class LexemeTripletAdmin(admin.ModelAdmin):
    list_display = ('get_text', 'get_meaning', 'get_gesture', 'moderation_status', 'created_by')
    list_filter = ['moderation_status', 'categories']
    search_fields = ('text_lexeme__text', 'meaning__description')
    autocomplete_fields = ['text_lexeme', 'meaning', 'gesture_lexeme']

    @admin.display(description='Текст')
    def get_text(self, obj):
        return str(obj.text_lexeme)

    @admin.display(description='Значение')
    def get_meaning(self, obj):
        return str(obj.meaning)[:30]

    @admin.display(description='Жест ID')
    def get_gesture(self, obj):
        return obj.gesture_lexeme_id

@admin.register(GestureRealization)
class GestureRealizationAdmin(admin.ModelAdmin):
    list_display = ['gesture_lexeme', 'author', 'is_primary', 'moderation_status', 'created_at']
    list_filter = ['is_primary', 'moderation_status', 'created_at']
    search_fields = ['gesture_lexeme__id', 'author__username']
    readonly_fields = ['created_at']