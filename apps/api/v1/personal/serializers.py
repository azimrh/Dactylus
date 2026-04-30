from rest_framework import serializers
from apps.dictionary.models import Personal, LexemePair


class PersonalListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для списка"""
    lexeme_pair_detail = serializers.SerializerMethodField()
    text_lexeme = serializers.SerializerMethodField()
    gesture_lexeme = serializers.SerializerMethodField()

    class Meta:
        model = Personal
        fields = [
            'id', 'lexeme_pair', 'lexeme_pair_detail',
            'text_lexeme', 'gesture_lexeme',
            'status', 'added_at', 'last_reviewed'
        ]
        read_only_fields = ['id', 'added_at', 'last_reviewed']

    def get_lexeme_pair_detail(self, obj):
        """Информация о паре"""
        return {
            'id': obj.lexeme_pair.id,
            'text': obj.lexeme_pair.text_lexeme.text,
            'gesture': obj.lexeme_pair.gesture_lexeme.text
        }

    def get_text_lexeme(self, obj):
        """Текстовая лемма"""
        return {
            'id': obj.lexeme_pair.text_lexeme.id,
            'text': obj.lexeme_pair.text_lexeme.text,
            'slug': obj.lexeme_pair.text_lexeme.slug
        }

    def get_gesture_lexeme(self, obj):
        """Жестовая лемма"""
        return {
            'id': obj.lexeme_pair.gesture_lexeme.id,
            'text': obj.lexeme_pair.gesture_lexeme.text,
            'slug': obj.lexeme_pair.gesture_lexeme.slug
        }


class PersonalDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор"""
    lexeme_pair_detail = serializers.SerializerMethodField()
    text_lexeme = serializers.SerializerMethodField()
    gesture_lexeme = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Personal
        fields = [
            'id', 'user', 'lexeme_pair', 'lexeme_pair_detail',
            'text_lexeme', 'gesture_lexeme',
            'status', 'notes', 'added_at', 'last_reviewed'
        ]
        read_only_fields = ['id', 'user', 'added_at', 'last_reviewed']

    def get_lexeme_pair_detail(self, obj):
        """Детальная информация о паре"""
        pair = obj.lexeme_pair
        return {
            'id': pair.id,
            'text_lexeme': {
                'id': pair.text_lexeme.id,
                'text': pair.text_lexeme.text,
                'slug': pair.text_lexeme.slug,
                'has_video': pair.gesture_lexeme.realizations.filter(
                    moderation_status='approved'
                ).exists()
            },
            'gesture_lexeme': {
                'id': pair.gesture_lexeme.id,
                'text': pair.gesture_lexeme.text,
                'slug': pair.gesture_lexeme.slug
            },
            'created_at': pair.created_at
        }

    def get_text_lexeme(self, obj):
        """Текстовая лемма с категориями"""
        lexeme = obj.lexeme_pair.text_lexeme
        return {
            'id': lexeme.id,
            'text': lexeme.text,
            'slug': lexeme.slug,
            'categories': list(lexeme.categories.values_list('name', flat=True))
        }

    def get_gesture_lexeme(self, obj):
        """Жестовая лемма с информацией о реализациях"""
        lexeme = obj.lexeme_pair.gesture_lexeme
        realizations = lexeme.realizations.filter(moderation_status='approved')
        return {
            'id': lexeme.id,
            'text': lexeme.text,
            'slug': lexeme.slug,
            'realizations_count': realizations.count(),
            'has_primary': realizations.filter(is_primary=True).exists()
        }


class PersonalCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления"""

    class Meta:
        model = Personal
        fields = ['lexeme_pair', 'status', 'notes']

    def validate_lexeme_pair(self, value):
        """Проверка, что пара существует и одобрена"""
        user = self.context['request'].user
        if value.moderation_status != 'approved':
            raise serializers.ValidationError(
                "Можно добавлять только одобренные пары лексем"
            )

        # Проверка на дубликат
        if Personal.objects.filter(user=user, lexeme_pair=value).exists():
            raise serializers.ValidationError(
                "Эта пара уже добавлена в ваш словарь"
            )

        return value


class PersonalStatisticsSerializer(serializers.Serializer):
    """Статистика изучения"""
    total = serializers.IntegerField()
    new = serializers.IntegerField()
    learning = serializers.IntegerField()
    learned = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    last_activity = serializers.DateTimeField(allow_null=True)