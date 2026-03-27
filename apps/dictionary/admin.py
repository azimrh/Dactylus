from django.contrib import admin

from .models import (
    Category,
    TextLexeme, # TextLexemeCompose, TextComposeItem,
    GestureLexeme, # GestureLexemeCompose, GestureComposeItem,
    LexemePair,
    GestureRealization,
    Meaning, LexemeMeaningMapping
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
    list_display = ('text', 'author', 'is_letter', 'created_at', 'is_published')
    search_fields = ('text',)
    list_filter = ('is_letter', 'is_published', 'categories')

'''
class TextComposeItemInline(admin.TabularInline):
    model = TextComposeItem
    extra = 1
    fk_name = 'compose'

@admin.register(TextLexemeCompose)
class TextLexemeComposeAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'created_at', 'is_published')
    search_fields = ('text',)
    inlines = [TextComposeItemInline]
'''

# -----------------------
# Жестовые леммы
# -----------------------

@admin.register(GestureLexeme)
class GestureLexemeAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'is_letter', 'created_at', 'is_published')
    search_fields = ('text',)
    list_filter = ('is_letter', 'is_published', 'categories')

'''
class GestureComposeItemInline(admin.TabularInline):
    model = GestureComposeItem
    extra = 1
    fk_name = 'compose'

@admin.register(GestureLexemeCompose)
class GestureLexemeComposeAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'created_at', 'is_published')
    search_fields = ('text',)
    inlines = [GestureComposeItemInline]
'''

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
    list_display = ('get_text_lexeme', 'get_gesture_lexeme', 'created_by', 'created_at', 'meaning', 'is_auto_meaning')
    search_fields = ('text_lexeme__text', 'gesture_lexeme__text')
    list_filter = ('is_auto_meaning',)

    def get_text_lexeme(self, obj):
        return str(obj.text_lexeme) if obj.text_lexeme else '-'

    get_text_lexeme.short_description = 'Текстовая лемма'

    def get_gesture_lexeme(self, obj):
        return str(obj.gesture_lexeme) if obj.gesture_lexeme else '-'

    get_gesture_lexeme.short_description = 'Жестовая лемма'
