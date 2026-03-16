from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.dictionary.models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('signs').all()
    serializer_class = CategorySerializer
