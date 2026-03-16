from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователя."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'role', 'bio']
        read_only_fields = ['id']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserProfileSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    avatar = serializers.ImageField(source='profile.avatar', read_only=True)
    bio = serializers.CharField(source='profile.bio', required=False)
    rating = serializers.IntegerField(source='profile.rating', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'hearing_status', 'region',
            'groups', 'is_verified',
            'avatar', 'bio', 'rating',
            'created_at'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'hearing_status', 'region']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        # Группа 'user' добавится через сигнал
        return user
