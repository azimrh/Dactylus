from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from apps.dictionary.models import Category, TextLexeme
from .serializers import (
    TextLexemeSerializer, TextLexemeListSerializer
)


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
