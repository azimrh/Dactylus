from django.contrib.auth import views as auth_views
from django.urls import path

from .views import page_news


urlpatterns = [
    path('news/', page_news, name='news')
]