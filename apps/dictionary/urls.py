from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.page_home, name='home'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.page_register, name='register'),

    path('dictionary/', views.page_dictionary, name='dictionary'),
    path('dictionary/category/<slug:slug>/', views.page_category, name='category'),
    path('dictionary/text/<slug:slug>/', views.page_text_lexeme, name='text_lexeme'),

    path('dictionary/add_category/', views.page_add_category, name='add-category'),
    path('dictionary/add_word/', views.page_add_word, name='add-word'),

    path('moderation/', views.moderation_home, name='moderation'),
    path('moderation/text/<int:pk>/', views.moderation_text_lexeme, name='moderation-text'),
    path('moderation/gesture/<int:pk>/', views.moderation_gesture_lexeme, name='moderation-gesture'),
    path('moderation/meaning/<int:pk>/', views.moderation_meaning, name='moderation-meaning'),
    path('moderation/pair/<int:pk>/', views.moderation_lexeme_pair, name='moderation-pair'),
    path('moderation/video/<int:pk>/', views.moderation_gesture_realization, name='moderation-video'),

    path('personal/', views.page_personal, name='personal'),

    path('translator/', views.page_home, name='translator'),
    path('search/', views.page_home, name='search'),
]