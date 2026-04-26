from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q

from apps.dictionary.models import Category, TextLexeme, Meaning
from .serializers import (
    TextLexemeSerializer, TextLexemeListSerializer,
    CategoryListSerializer, CategoryDetailSerializer, CategoryTreeSerializer,
    MeaningListSerializer, MeaningDetailSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.annotate(
        words_count=Count(
            'lexemepair__text_lexeme',
            filter=Q(lexemepair__moderation_status='approved'),
            distinct=True
        ),
        gestures_count=Count(
            'lexemepair__gesture_lexeme',
            filter=Q(lexemepair__moderation_status='approved'),
            distinct=True
        ),
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
            words_count=Count(
                'lexemepair__text_lexeme',
                filter=Q(lexemepair__moderation_status='approved'),
                distinct=True
            ),
            gestures_count=Count(
                'lexemepair__gesture_lexeme',
                filter=Q(lexemepair__moderation_status='approved'),
                distinct=True
            ),
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


class MeaningViewSet(viewsets.ReadOnlyModelViewSet):
    """API для значений (денотатов)"""
    queryset = Meaning.objects.select_related('author').prefetch_related(
        'textlexeme_set',
        'gesturelexeme_set'
    ).order_by('-created_at')

    serializer_class = MeaningListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['description']
    ordering_fields = ['created_at', 'id']
    lookup_field = 'pk'

    def get_serializer_class(self):
        """Динамический выбор сериализатора"""
        if self.action == 'list':
            return MeaningListSerializer
        if self.action == 'retrieve':
            return MeaningDetailSerializer
        return MeaningListSerializer

    def get_queryset(self):
        """Фильтрация по статусу модерации"""
        queryset = self.queryset
        moderation_status = self.request.query_params.get('status')
        if moderation_status:
            queryset = queryset.filter(moderation_status=moderation_status)
        return queryset

    @action(detail=False, methods=['get'])
    def approved(self, request):
        """Только одобренные значения"""
        meanings = self.get_queryset().filter(moderation_status='approved')
        serializer = MeaningListSerializer(meanings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def lexemes(self, request, pk=None):
        """Получить все лексемы для данного значения"""
        meaning = self.get_object()
        data = {
            'text_lexemes': [
                {'id': lexeme.id, 'text': lexeme.text, 'slug': lexeme.slug}
                for lexeme in meaning.textlexeme_set.all()
            ],
            'gesture_lexemes': [
                {'id': lexeme.id, 'text': lexeme.text, 'slug': lexeme.slug}
                for lexeme in meaning.gesturelexeme_set.all()
            ]
        }
        return Response(data)