import django_filters
from django.db.models import Q

from apps.dictionary.models import TextLexeme, GestureLexeme, Category


class CategoryFilter(django_filters.FilterSet):
    """Фильтры для категорий"""
    parent = django_filters.CharFilter(field_name='parent__slug', lookup_expr='iexact')
    is_root = django_filters.BooleanFilter(field_name='parent', lookup_expr='isnull')
    name_start = django_filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Category
        fields = ['order', 'parent']


class TextLexemeFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='categories__slug', lookup_expr='iexact')
    letter = django_filters.CharFilter(field_name='letter_char', lookup_expr='iexact')
    is_letter = django_filters.BooleanFilter()
    text_start = django_filters.CharFilter(field_name='text', lookup_expr='istartswith')

    class Meta:
        model = TextLexeme
        fields = ['is_published', 'is_letter', 'categories']


class GestureLexemeFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='categories__slug', lookup_expr='iexact')
    letter = django_filters.CharFilter(field_name='letter_char', lookup_expr='iexact')
    is_letter = django_filters.BooleanFilter()
    has_video = django_filters.BooleanFilter(method='filter_has_video')

    class Meta:
        model = GestureLexeme
        fields = ['is_published', 'is_letter', 'categories']

    def filter_has_video(self, queryset, name, value):
        if value:
            return queryset.exclude(video='').exclude(video__isnull=True)
        return queryset.filter(Q(video='') | Q(video__isnull=True))
