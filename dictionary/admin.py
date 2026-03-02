from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Category, Meaning, TextLemma, GestureLemma,
    TextMeaningMapping, GestureMeaningMapping,
    SynonymRelation, AntonymRelation,
    TextExplanation, GestureExplanation,
    TextExample, GestureExample,
    InvariantEvaluation, HomonymDisambiguation,
    PersonalDictionary, TranslationCache, News
)


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
    list_display = ['name', 'is_published', 'is_dialectal', 'region', 'created_at']
    list_filter = ['is_published', 'is_dialectal', 'categories', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['categories', 'related_lemmas']
    inlines = [TextMeaningMappingInline]


@admin.register(GestureLemma)
class GestureLemmaAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_published', 'is_dialectal', 'region', 'created_at']
    list_filter = ['is_published', 'is_dialectal', 'created_at']
    search_fields = ['name', 'technical_description']
    filter_horizontal = ['related_lemmas']
    inlines = [GestureMeaningMappingInline]


@admin.register(TextMeaningMapping)
class TextMeaningMappingAdmin(admin.ModelAdmin):
    list_display = ['text_lemma', 'meaning', 'is_primary', 'usage_preference_score']
    list_filter = ['is_primary']
    search_fields = ['text_lemma__name', 'meaning__description']
    autocomplete_fields = ['text_lemma', 'meaning']


@admin.register(GestureMeaningMapping)
class GestureMeaningMappingAdmin(admin.ModelAdmin):
    list_display = ['gesture_lemma', 'meaning', 'is_primary', 'usage_preference_score']
    list_filter = ['is_primary']
    search_fields = ['gesture_lemma__name', 'meaning__description']
    autocomplete_fields = ['gesture_lemma', 'meaning']


@admin.register(SynonymRelation)
class SynonymRelationAdmin(admin.ModelAdmin):
    list_display = ['from_lemma', 'to_lemma']
    search_fields = ['from_lemma__name', 'to_lemma__name']
    autocomplete_fields = ['from_lemma', 'to_lemma']


@admin.register(AntonymRelation)
class AntonymRelationAdmin(admin.ModelAdmin):
    list_display = ['from_lemma', 'to_lemma']
    search_fields = ['from_lemma__name', 'to_lemma__name']
    autocomplete_fields = ['from_lemma', 'to_lemma']


@admin.register(TextExplanation)
class TextExplanationAdmin(admin.ModelAdmin):
    list_display = ['meaning_short', 'is_primary', 'raw_text_short', 'author', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['raw_text', 'meaning__description']
    autocomplete_fields = ['meaning', 'author']

    def meaning_short(self, obj):
        return obj.meaning.description[:40]
    meaning_short.short_description = 'Смысл'

    def raw_text_short(self, obj):
        return obj.raw_text[:50]
    raw_text_short.short_description = 'Текст'


@admin.register(GestureExplanation)
class GestureExplanationAdmin(admin.ModelAdmin):
    list_display = ['meaning_short', 'is_primary', 'author', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['meaning__description']
    autocomplete_fields = ['meaning', 'author']

    def meaning_short(self, obj):
        return obj.meaning.description[:40]
    meaning_short.short_description = 'Смысл'


@admin.register(TextExample)
class TextExampleAdmin(admin.ModelAdmin):
    list_display = ['meaning_short', 'raw_text_short', 'situation', 'author', 'created_at']
    list_filter = ['situation', 'created_at']
    search_fields = ['raw_text', 'meaning__description']
    autocomplete_fields = ['meaning', 'author']

    def meaning_short(self, obj):
        return obj.meaning.description[:40]
    meaning_short.short_description = 'Смысл'

    def raw_text_short(self, obj):
        return obj.raw_text[:50]
    raw_text_short.short_description = 'Текст'


@admin.register(GestureExample)
class GestureExampleAdmin(admin.ModelAdmin):
    list_display = ['meaning_short', 'situation', 'author', 'created_at']
    list_filter = ['situation', 'created_at']
    search_fields = ['meaning__description']
    autocomplete_fields = ['meaning', 'author']

    def meaning_short(self, obj):
        return obj.meaning.description[:40]
    meaning_short.short_description = 'Смысл'


@admin.register(InvariantEvaluation)
class InvariantEvaluationAdmin(admin.ModelAdmin):
    list_display = ['target_lemma', 'replacement_lemma', 'answer', 'situation', 'user', 'created_at']
    list_filter = ['answer', 'situation', 'created_at']
    search_fields = ['phrase_text', 'target_lemma__name', 'replacement_lemma__name']
    autocomplete_fields = ['target_lemma', 'replacement_lemma', 'user']


@admin.register(HomonymDisambiguation)
class HomonymDisambiguationAdmin(admin.ModelAdmin):
    list_display = ['text_lemma', 'meaning_short', 'example_text_short', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['example_text', 'text_lemma__name', 'meaning__description']
    autocomplete_fields = ['text_lemma', 'meaning', 'user']

    def meaning_short(self, obj):
        return obj.meaning.description[:40]
    meaning_short.short_description = 'Смысл'

    def example_text_short(self, obj):
        return obj.example_text[:50]
    example_text_short.short_description = 'Пример'


@admin.register(PersonalDictionary)
class PersonalDictionaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'lemma_display', 'meaning_short', 'proficiency', 'practice_count', 'last_practiced']
    list_filter = ['proficiency', 'added_at']
    search_fields = ['user__username', 'text_lemma__name', 'gesture_lemma__name']
    autocomplete_fields = ['user', 'text_lemma', 'gesture_lemma', 'meaning']

    def lemma_display(self, obj):
        if obj.text_lemma:
            return f"Т: {obj.text_lemma.name}"
        elif obj.gesture_lemma:
            return f"Ж: {obj.gesture_lemma.name}"
        return "-"
    lemma_display.short_description = 'Лемма'

    def meaning_short(self, obj):
        if obj.meaning:
            return obj.meaning.description[:40]
        return "-"
    meaning_short.short_description = 'Смысл'


@admin.register(TranslationCache)
class TranslationCacheAdmin(admin.ModelAdmin):
    list_display = ['text_input_short', 'user', 'is_personalized', 'created_at']
    list_filter = ['is_personalized', 'created_at']
    search_fields = ['text_input']
    autocomplete_fields = ['user']

    def text_input_short(self, obj):
        return obj.text_input[:50]
    text_input_short.short_description = 'Входной текст'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'published_at', 'author']
    list_filter = ['is_published', 'published_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)} if hasattr(News, 'slug') else {}
    autocomplete_fields = ['author']
