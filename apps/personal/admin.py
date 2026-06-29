from django.contrib import admin

from apps.personal.models import Personal


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('user', 'lexeme_pair', 'status', 'added_at', 'last_reviewed')
    list_filter = ('status', 'added_at')
    search_fields = (
        'user__username',
        'user__email',
        'notes',
        'lexeme_pair__text_lexeme__text',
        'lexeme_pair__gesture_lexeme__text'
    )
    date_hierarchy = 'added_at'
    readonly_fields = ('added_at', 'last_reviewed')
    raw_id_fields = ('user', 'lexeme_pair')

    fieldsets = (
        (None, {
            'fields': ('user', 'lexeme_pair')
        }),
        ('Статус изучения', {
            'fields': ('status', 'notes', 'last_reviewed')
        }),
        ('Даты', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user',
            'lexeme_pair'
        )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            from django.db.models import Q
            queryset |= self.model.objects.filter(
                Q(lexeme_pair__text_lexeme__text__icontains=search_term) |
                Q(lexeme_pair__gesture_lexeme__text__icontains=search_term) |
                Q(lexeme_pair__id__icontains=search_term)
            )
        return queryset, use_distinct
