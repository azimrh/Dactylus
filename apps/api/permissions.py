from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только владелец может редактировать.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Только преподаватели и админы.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['teacher', 'admin'] or
            request.user.is_staff
        )
