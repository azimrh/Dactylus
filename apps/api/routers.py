from rest_framework.routers import DefaultRouter

from .v1.users.views import UserViewSet
from .v1.dictionary.views import CategoryViewSet, TextLexemeViewSet, MeaningViewSet
from .v1.personal.views import PersonalViewSet

router = DefaultRouter()


# Users
router.register(r'users', UserViewSet, basename='user')

# Dictionary
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'text-lexemes', TextLexemeViewSet, basename='text_lexeme')
router.register(r'meanings', MeaningViewSet, basename='meaning')

# Personal (требует авторизации)
router.register(r'personal', PersonalViewSet, basename='personal')
