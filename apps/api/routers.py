from rest_framework.routers import DefaultRouter

from .v1.users.views import UserViewSet
from .v1.dictionary.views import CategoryViewSet, TextLexemeViewSet, MeaningViewSet
from .v1.personal.views import PersonalViewSet
from .v1.news.views import NewsViewSet


router = DefaultRouter()

# Users
router.register(r'users', UserViewSet, basename='user')

# Dictionary
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'text-lexemes', TextLexemeViewSet, basename='text_lexeme')
router.register(r'meanings', MeaningViewSet, basename='meaning')

# Personal (требует авторизации)
router.register(r'personal', PersonalViewSet, basename='personal')

# News
router.register(r'news', NewsViewSet, basename='news')