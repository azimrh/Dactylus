from rest_framework import serializers
from apps.dictionary.models import Category


class CategoryChildSerializer(serializers.ModelSerializer):
    """Вложенные дочерние категории (рекурсивно)"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'order', 'children']

    def get_children(self, obj):
        if hasattr(obj, 'children'):
            return CategoryChildSerializer(obj.children.all(), many=True).data
        return []


class CategorySerializer(serializers.ModelSerializer):
    """Основной сериализатор категории с родителем и детьми"""
    parent = CategoryChildSerializer(read_only=True)
    children = CategoryChildSerializer(many=True, read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'children', 'order', 'url']


class CategoryMinimalSerializer(serializers.ModelSerializer):
    """Минимальная версия для вложенного использования"""

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
