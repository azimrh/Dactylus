import django_filters
from django.db import models
from apps.dictionary.models import Category


class CategoryFilter(django_filters.FilterSet):
    parent = django_filters.CharFilter(field_name='parent__slug', lookup_expr='iexact')
    is_root = django_filters.BooleanFilter(field_name='parent', lookup_expr='isnull')
    name_start = django_filters.CharFilter(field_name='name', lookup_expr='istartswith')

    # Поиск по подстроке в названии (case-insensitive)
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    # Или универсальный поиск по названию и описанию
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Category
        fields = ['order', 'parent', 'name', 'search', 'is_root']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value)
        )
