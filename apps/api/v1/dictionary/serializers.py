from rest_framework import serializers
from apps.dictionary.models import Category, TextLexeme, Meaning


class CategoryListSerializer(serializers.ModelSerializer):
    """Короткий сериализатор категорий"""
    words_count = serializers.IntegerField(read_only=True)
    gestures_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'words_count', 'gestures_count']


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор категории с дочерними"""
    parent = CategoryListSerializer(read_only=True)
    children = CategoryListSerializer(many=True, read_only=True)
    words_count = serializers.IntegerField(read_only=True)
    gestures_count = serializers.IntegerField(read_only=True)
    path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'children',
                  'words_count', 'gestures_count', 'order', 'path']

    def get_path(self, obj):
        """Возвращает путь от корня до текущей категории"""
        path = []
        current = obj
        while current.parent:
            path.insert(0, {'name': current.parent.name, 'slug': current.parent.slug})
            current = current.parent
        return path


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Сериализатор для древовидной структуры (вложенные дети)"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'order', 'children']

    def get_children(self, obj):
        """Рекурсивно сериализуем дочерние категории"""
        children = obj.children.all()
        if children.exists():
            return CategoryTreeSerializer(children, many=True).data
        return []


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


# Meanings

class MeaningListSerializer(serializers.ModelSerializer):
    """Короткий сериализатор значений"""

    class Meta:
        model = Meaning
        fields = ['id', 'description', 'moderation_status', 'created_at']


class MeaningDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор значения с лексемами"""
    text_lexemes = serializers.SerializerMethodField()
    gesture_lexemes = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Meaning
        fields = ['id', 'description', 'moderation_status',
                  'author_name', 'created_at',
                  'text_lexemes', 'gesture_lexemes']

    def get_text_lexemes(self, obj):
        """Получить связанные текстовые леммы"""
        return [
            {'id': lexeme.id, 'text': lexeme.text, 'slug': lexeme.slug}
            for lexeme in obj.textlexeme_set.filter(moderation_status='approved')
        ]

    def get_gesture_lexemes(self, obj):
        """Получить связанные жестовые леммы"""
        return [
            {'id': lexeme.id, 'text': lexeme.text, 'slug': lexeme.slug}
            for lexeme in obj.gesturelexeme_set.filter(moderation_status='approved')
        ]