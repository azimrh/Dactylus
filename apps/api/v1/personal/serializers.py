from rest_framework import serializers

from apps.personal.models import Personal


class PersonalListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для списка"""
    lexeme_triplet_detail = serializers.SerializerMethodField()
    text_lexeme = serializers.SerializerMethodField()
    gesture_lexeme = serializers.SerializerMethodField()

    class Meta:
        model = Personal
        fields = [
            'id', 'lexeme_triplet', 'lexeme_triplet_detail',
            'text_lexeme', 'gesture_lexeme',
            'status', 'added_at', 'last_reviewed'
        ]
        read_only_fields = ['id', 'added_at', 'last_reviewed']

    def get_lexeme_triplet_detail(self, obj):
        """Информация о триплете"""
        triplet = obj.lexeme_triplet
        return {
            'id': triplet.id,
            'text': triplet.text_lexeme.text,
            'gesture': triplet.gesture_lexeme.text
        }

    def get_text_lexeme(self, obj):
        """Текстовая лемма"""
        return {
            'id': obj.lexeme_triplet.text_lexeme.id,
            'text': obj.lexeme_triplet.text_lexeme.text,
            'slug': obj.lexeme_triplet.text_lexeme.slug
        }

    def get_gesture_lexeme(self, obj):
        """Жестовая лемма"""
        return {
            'id': obj.lexeme_triplet.gesture_lexeme.id,
            'text': obj.lexeme_triplet.gesture_lexeme.text,
            'slug': obj.lexeme_triplet.gesture_lexeme.slug
        }


class PersonalDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор"""
    lexeme_triplet_detail = serializers.SerializerMethodField()
    text_lexeme = serializers.SerializerMethodField()
    gesture_lexeme = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Personal
        fields = [
            'id', 'user', 'lexeme_triplet', 'lexeme_triplet_detail',
            'text_lexeme', 'gesture_lexeme',
            'status', 'notes', 'added_at', 'last_reviewed'
        ]
        read_only_fields = ['id', 'user', 'added_at', 'last_reviewed']

    def get_lexeme_triplet_detail(self, obj):
        """Детальная информация о триплете"""
        triplet = obj.lexeme_triplet
        return {
            'id': triplet.id,
            'text_lexeme': {
                'id': triplet.text_lexeme.id,
                'text': triplet.text_lexeme.text,
                'slug': triplet.text_lexeme.slug,
                'has_video': triplet.gesture_lexeme.realizations.filter(
                    moderation_status='approved'
                ).exists()
            },
            'gesture_lexeme': {
                'id': triplet.gesture_lexeme.id,
                'text': triplet.gesture_lexeme.text,
                'slug': triplet.gesture_lexeme.slug
            },
            'created_at': triplet.created_at
        }

    def get_text_lexeme(self, obj):
        """Текстовая лемма с категориями"""
        lexeme = obj.lexeme_triplet.text_lexeme
        return {
            'id': lexeme.id,
            'text': lexeme.text,
            'slug': lexeme.slug,
            'categories': list(lexeme.categories.values_list('name', flat=True))
        }

    def get_gesture_lexeme(self, obj):
        """Жестовая лемма с информацией о реализациях"""
        lexeme = obj.lexeme_triplet.gesture_lexeme
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
        fields = ['lexeme_triplet', 'status', 'notes']

    def validate_lexeme_triplet(self, value):
        """Проверка, что триплет существует и одобрен"""
        user = self.context['request'].user
        if value.moderation_status != 'approved':
            raise serializers.ValidationError(
                "Можно добавлять только одобренные триплеты"
            )

        # Проверка на дубликат
        if Personal.objects.filter(user=user, lexeme_triplet=value).exists():
            raise serializers.ValidationError(
                "Этот триплет уже добавлен в ваш словарь"
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