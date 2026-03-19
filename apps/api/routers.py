from rest_framework.routers import DefaultRouter

from .v1.users.views import UserViewSet
from .v1.dictionary.views import CategoryViewSet

router = DefaultRouter()


# Users
router.register(r'users', UserViewSet, basename='user')

# Dictionary
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
