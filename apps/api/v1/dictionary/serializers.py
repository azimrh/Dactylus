from rest_framework import serializers
from apps.dictionary.models import Category, TextLexeme, Meaning, LexemeTriplet, GestureLexeme


class CategoryListSerializer(serializers.ModelSerializer):
    """Короткий сериализатор категорий"""
    # Поля words_count и gestures_count теперь считаются через lexemetriplet
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

    # Убрана связь categories и meanings, так как они теперь опосредованы через Triplet
    # Если нужно показать категории, придется делать SerializerMethodField или prefetch через triplets

    class Meta:
        model = TextLexeme
        fields = ['id', 'text', 'slug']  # Убраны categories и meanings


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
        """Получить связанные текстовые леммы через триплеты"""
        # Используем related_name 'triplets' из модели LexemeTriplet
        triplets = obj.triplets.filter(moderation_status='approved').select_related('text_lexeme')
        return [
            {'id': t.text_lexeme.id, 'text': t.text_lexeme.text, 'slug': t.text_lexeme.slug}
            for t in triplets
        ]

    def get_gesture_lexemes(self, obj):
        """Получить связанные жестовые леммы через триплеты"""
        triplets = obj.triplets.filter(moderation_status='approved').select_related('gesture_lexeme')
        return [
            {'id': t.gesture_lexeme.id, 'label': f"Gesture #{t.gesture_lexeme.id}"}  # У жеста больше нет текста
            for t in triplets
        ]