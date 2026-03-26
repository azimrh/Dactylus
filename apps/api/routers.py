from rest_framework.routers import DefaultRouter

from .v1.users.views import UserViewSet
from .v1.dictionary.views import TextLexemeViewSet

router = DefaultRouter()


# Users
router.register(r'users', UserViewSet, basename='user')

# Dictionary
router = DefaultRouter()
router.register(r'text-lexemes', TextLexemeViewSet, basename='text_lexeme')
