from django.urls import path
from . import views


urlpatterns = [
    path('', views.page_news, name='news'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
    path('create/', views.news_create, name='news_create'),
    path('<int:pk>/delete/', views.news_delete, name='news_delete'),
]