from django.contrib import admin
from apps.personal.models import Personal


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_text', 'get_gesture_id', 'status', 'added_at', 'last_reviewed')
    list_filter = ('status', 'added_at')
    search_fields = (
        'user__username',
        'user__email',
        'notes',
        'lexeme_triplet__text_lexeme__text',
    )
    date_hierarchy = 'added_at'
    readonly_fields = ('added_at', 'last_reviewed')
    raw_id_fields = ('user', 'lexeme_triplet')
    fieldsets = (
        (None, {
            'fields': ('user', 'lexeme_triplet')
        }),
        ('Статус изучения', {
            'fields': ('status', 'notes', 'last_reviewed')
        }),
        ('Даты', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Текст')
    def get_text(self, obj):
        return obj.lexeme_triplet.text_lexeme.text if obj.lexeme_triplet else '-'

    @admin.display(description='Жест ID')
    def get_gesture_id(self, obj):
        return obj.lexeme_triplet.gesture_lexeme_id if obj.lexeme_triplet else '-'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user',
            'lexeme_triplet__text_lexeme',
            'lexeme_triplet__gesture_lexeme'
        )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            from django.db.models import Q
            # Поиск по тексту связанной текстовой леммы
            queryset |= self.model.objects.filter(
                Q(lexeme_triplet__text_lexeme__text__icontains=search_term) |
                Q(lexeme_triplet__id__icontains=search_term)
            )
        return queryset, use_distinct