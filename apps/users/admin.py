from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserStats


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class StatsInline(admin.StackedInline):
    model = UserStats
    can_delete = False
    readonly_fields = [f.name for f in UserStats._meta.fields]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'hearing_status',
        'get_groups', 'is_verified', 'rating', 'created_at'
    ]
    list_filter = [
        'hearing_status', 'is_verified',
        'groups', 'created_at'
    ]
    filter_horizontal = ['groups', 'user_permissions']  # Удобный виджет
    search_fields = ['username', 'email', 'region']
    inlines = [ProfileInline, StatsInline]

    fieldsets = BaseUserAdmin.fieldsets + (
        ('РЖЯ Профиль', {
            'fields': ('hearing_status', 'is_verified', 'region', 'primary_group')
        }),
    )

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()[:3]])
    get_groups.short_description = 'Группы'

    def rating(self, obj):
        return obj.profile.rating if hasattr(obj, 'profile') else 0
    rating.admin_order_field = 'profile__rating'
