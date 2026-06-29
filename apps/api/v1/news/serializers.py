from rest_framework import serializers

from apps.news.models import News


class NewsListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для списка новостей"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'excerpt', 'image',
            'is_published', 'published_at', 'author_name'
        ]
        read_only_fields = ['id', 'published_at', 'author_name']

    def get_excerpt(self, obj):
        """Краткое содержание — первые 200 символов"""
        return obj.content[:200] + '...' if len(obj.content) > 200 else obj.content


class NewsDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор новости"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'image',
            'is_published', 'published_at',
            'author', 'author_name', 'author_avatar'
        ]
        read_only_fields = ['id', 'published_at', 'author_name', 'author_avatar']

    def get_author_avatar(self, obj):
        """URL аватара автора"""
        if hasattr(obj.author, 'profile') and obj.author.profile.avatar:
            return obj.author.profile.avatar.url
        return None


class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления новости"""
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = News
        fields = ['title', 'content', 'image', 'is_published']

    def validate_title(self, value):
        """Валидация заголовка"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Заголовок должен содержать минимум 3 символа"
            )
        return value.strip()

    def validate_content(self, value):
        """Валидация содержания"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Содержание должно содержать минимум 10 символов"
            )
        return value.strip()
