from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Case, When, IntegerField
from django.utils import timezone

from apps.dictionary.models import Personal
from .serializers import (
    PersonalListSerializer,
    PersonalDetailSerializer,
    PersonalCreateUpdateSerializer,
    PersonalStatisticsSerializer
)


class PersonalViewSet(viewsets.ModelViewSet):
    """
    ViewSet для личного словаря пользователя.
    Требует авторизации.
    """
    serializer_class = PersonalListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['added_at', 'last_reviewed', 'status']
    ordering = ['-added_at']
    search_fields = [
        'lexeme_pair__text_lexeme__text',
        'lexeme_pair__gesture_lexeme__text',
        'notes'
    ]

    def get_serializer_class(self):
        """Динамический выбор сериализатора"""
        if self.action in ['create', 'update', 'partial_update']:
            return PersonalCreateUpdateSerializer
        if self.action == 'retrieve':
            return PersonalDetailSerializer
        if self.action == 'statistics':
            return PersonalStatisticsSerializer
        return PersonalListSerializer

    def get_queryset(self):
        """Только записи текущего пользователя"""
        return Personal.objects.filter(
            user=self.request.user
        ).select_related(
            'lexeme_pair__text_lexeme',
            'lexeme_pair__gesture_lexeme'
        ).prefetch_related(
            'lexeme_pair__gesture_lexeme__realizations'
        )

    def perform_create(self, serializer):
        """При создании автоматически устанавливаем пользователя"""
        serializer.save(user=self.request.user, last_reviewed=timezone.now())

    def perform_update(self, serializer):
        """При обновлении статуса обновляем время последнего просмотра"""
        if 'status' in serializer.validated_data:
            serializer.save(last_reviewed=timezone.now())
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика изучения для текущего пользователя"""
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total=Count('id'),
            new=Count('id', filter=Q(status='new')),
            learning=Count('id', filter=Q(status='learning')),
            learned=Count('id', filter=Q(status='learned'))
        )

        # Вычисляем процент прогресса
        total = stats['total']
        progress = (stats['learned'] / total * 100) if total > 0 else 0

        # Последняя активность
        last_entry = queryset.order_by('-last_reviewed').first()

        data = {
            'total': total,
            'new': stats['new'],
            'learning': stats['learning'],
            'learned': stats['learned'],
            'progress_percentage': round(progress, 1),
            'last_activity': last_entry.last_reviewed if last_entry else None
        }

        serializer = PersonalStatisticsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Фильтрация по статусу"""
        status_filter = request.query_params.get('status', 'new')
        if status_filter not in ['new', 'learning', 'learned']:
            return Response(
                {'error': 'Неверный статус. Допустимые значения: new, learning, learned'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(status=status_filter)

        # Пагинация
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_learned(self, request, pk=None):
        """Отметить как выученное"""
        instance = self.get_object()
        instance.status = 'learned'
        instance.last_reviewed = timezone.now()
        instance.save()
        return Response({'status': 'learned'})

    @action(detail=True, methods=['post'])
    def reset_status(self, request, pk=None):
        """Сбросить статус на 'новое'"""
        instance = self.get_object()
        instance.status = 'new'
        instance.last_reviewed = timezone.now()
        instance.save()
        return Response({'status': 'new'})
