from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from apps.news.models import News
from .serializers import (
    NewsListSerializer,
    NewsDetailSerializer,
    NewsCreateUpdateSerializer
)


class IsAuthorOrAdmin(permissions.BasePermission):
    """
    Разрешение: только автор или админ/модератор может редактировать/удалять.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user or
            request.user.is_staff or
            request.user.groups.filter(name__in=['moderator', 'admin']).exists()
        )


class NewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для новостей.
    - Анонимы видят только опубликованные новости
    - Авторизованные пользователи могут создавать новости
    - Автор/админ/модератор может редактировать и удалять
    """
    serializer_class = NewsListSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['published_at', 'title']
    ordering = ['-published_at']
    search_fields = ['title', 'content']
    lookup_field = 'pk'

    def get_permissions(self):
        """Динамическое определение прав"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [
                permissions.IsAuthenticated(),
                IsAuthorOrAdmin()
            ]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        """Динамический выбор сериализатора"""
        if self.action in ['create', 'update', 'partial_update']:
            return NewsCreateUpdateSerializer
        if self.action == 'retrieve':
            return NewsDetailSerializer
        return NewsListSerializer

    def get_queryset(self):
        """
        Фильтрация новостей:
        - Анонимы и обычные пользователи: только опубликованные
        - Авторизованные: видят свои неопубликованные + все опубликованные
        - Админы/модераторы: все новости
        """
        user = self.request.user

        # Админы и модераторы видят всё
        if user.is_authenticated and (
            user.is_staff or
            user.groups.filter(name__in=['moderator', 'admin']).exists()
        ):
            return News.objects.all().select_related('author', 'author__profile')

        # Авторизованные пользователи: свои черновики + все опубликованные
        if user.is_authenticated:
            return News.objects.filter(
                Q(is_published=True) | Q(author=user)
            ).select_related('author', 'author__profile')

        # Анонимы: только опубликованные
        return News.objects.filter(
            is_published=True
        ).select_related('author', 'author__profile')

    def perform_create(self, serializer):
        """При создании автоматически устанавливаем автора"""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """При обновлении обновляем published_at если публикуем"""
        instance = self.get_object()
        was_published = instance.is_published
        is_published = serializer.validated_data.get('is_published', was_published)

        # Если новость публикуется впервые — обновляем published_at
        if not was_published and is_published:
            serializer.save(published_at=timezone.now())
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Последние опубликованные новости (по умолчанию 5)"""
        limit = int(request.query_params.get('limit', 5))
        limit = min(limit, 20)  # Максимум 20

        queryset = News.objects.filter(
            is_published=True
        ).select_related('author').order_by('-published_at')[:limit]

        serializer = NewsListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_author(self, request):
        """Новости конкретного автора"""
        author_id = request.query_params.get('author_id')
        if not author_id:
            return Response(
                {'error': 'Параметр author_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            author_id = int(author_id)
        except ValueError:
            return Response(
                {'error': 'author_id должен быть числом'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(author_id=author_id)

        # Пагинация
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unpublished(self, request):
        """Неопубликованные новости (только для админов/модераторов/авторов)"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Требуется авторизация'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        queryset = News.objects.filter(is_published=False)

        # Обычные пользователи видят только свои неопубликованные
        if not (
            request.user.is_staff or
            request.user.groups.filter(name__in=['moderator', 'admin']).exists()
        ):
            queryset = queryset.filter(author=request.user)

        # Пагинация
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Опубликовать новость (только автор/админ/модератор)"""
        instance = self.get_object()

        # Проверка прав через IsAuthorOrAdmin
        if not (
            instance.author == request.user or
            request.user.is_staff or
            request.user.groups.filter(name__in=['moderator', 'admin']).exists()
        ):
            return Response(
                {'error': 'Нет прав на публикацию'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.is_published = True
        instance.published_at = timezone.now()
        instance.save()

        serializer = NewsDetailSerializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Снять с публикации (только автор/админ/модератор)"""
        instance = self.get_object()

        if not (
            instance.author == request.user or
            request.user.is_staff or
            request.user.groups.filter(name__in=['moderator', 'admin']).exists()
        ):
            return Response(
                {'error': 'Нет прав на снятие с публикации'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.is_published = False
        instance.save()

        serializer = NewsDetailSerializer(instance)
        return Response(serializer.data)