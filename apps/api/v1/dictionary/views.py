from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q

from apps.dictionary.models import Category, TextLexeme
from .serializers import (
    TextLexemeSerializer, TextLexemeListSerializer,
    CategoryListSerializer, CategoryDetailSerializer, CategoryTreeSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.annotate(
        words_count=Count('textlexeme', filter=Q(textlexeme__is_published=True), distinct=True),
        gestures_count=Count('gesturelexeme', filter=Q(gesturelexeme__is_published=True), distinct=True),
    ).order_by('order', 'name')

    serializer_class = CategoryListSerializer
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        if self.action == 'tree':
            return CategoryTreeSerializer
        return CategoryListSerializer

    def get_queryset(self):
        if self.action == 'list':
            # Только корневые категории для списка
            return self.queryset.filter(parent__isnull=True)
        return self.queryset

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Все категории в виде дерева"""
        root_categories = Category.objects.filter(parent__isnull=True).order_by('order', 'name')
        serializer = CategoryTreeSerializer(root_categories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def children(self, request, slug=None):
        """Прямые дочерние категории"""
        category = self.get_object()
        children = category.children.annotate(
            words_count=Count('textlexeme', filter=Q(textlexeme__is_published=True), distinct=True),
            gestures_count=Count('gesturelexeme', filter=Q(gesturelexeme__is_published=True), distinct=True),
        ).order_by('order', 'name')
        serializer = CategoryListSerializer(children, many=True)
        return Response(serializer.data)


class TextLexemeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TextLexeme.objects.all()
    serializer_class = TextLexemeSerializer
    filter_backends = [SearchFilter]
    search_fields = ['text', 'slug']
    ordering_fields = ['text', 'id']

    def get_serializer_class(self):
        """Динамический выбор сериализатора"""
        if self.action == 'list':
            return TextLexemeListSerializer
        if self.action == 'retrieve':
            return TextLexemeSerializer
        return TextLexemeSerializer
