from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.page_home, name='home'),

    path('dictionary/', views.page_dictionary, name='dictionary'),
    path('dictionary/category/<slug:slug>/', views.page_category, name='category'),
    path('dictionary/text/<slug:slug>/', views.page_text_lexeme, name='text_lexeme'),

    path('dictionary/add_category/', views.page_add_category, name='add-category'),
    path('dictionary/add_word/', views.page_add_word, name='add-word'),
]