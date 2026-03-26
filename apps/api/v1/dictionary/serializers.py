from rest_framework import serializers
from apps.dictionary.models import Category, TextLexeme


# Text Lexemes

class TextLexemeSerializer(serializers.ModelSerializer):
    """Основной сериализатор текстовых лексем"""
    categories = serializers.StringRelatedField(many=True, read_only=True)
    meanings = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = TextLexeme
        fields = ['id', 'text', 'slug', 'categories', 'meanings']

class TextLexemeListSerializer(serializers.ModelSerializer):
    """Короткий сериализатор текстовых лексем"""

    class Meta:
        model = TextLexeme
        fields = ['id', 'text', 'slug']
