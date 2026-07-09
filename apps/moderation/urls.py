from django.urls import path
from . import views

urlpatterns = [
    path('', views.moderation_home, name='moderation'),
    path('text/<int:pk>/', views.moderation_text_lexeme, name='moderation-text'),
    path('meaning/<int:pk>/', views.moderation_meaning, name='moderation-meaning'),
    path('gesture/<int:pk>/', views.moderation_home, name='moderation'),
    path('triplet/<int:pk>/', views.moderation_lexeme_triplet, name='moderation-triplet'),
    path('video/<int:pk>/', views.moderation_gesture_realization, name='moderation-video')
]