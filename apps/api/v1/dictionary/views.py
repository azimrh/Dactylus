from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.dictionary.models import Category
from .serializers import CategorySerializer
from .filters import CategoryFilter  # Импорт фильтра


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter  # Явное подключение фильтра
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['name', 'order', 'id']
    ordering = ['order', 'name']
