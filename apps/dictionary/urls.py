from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    path('dictionary/', views.dictionary, name='dictionary'),
    path('dictionary/category/<slug:slug>/', views.category, name='category'),
    path('dictionary/text/<slug:slug>/', views.text_lexeme, name='text_lemma'),

    path('dictionary/add_category/', views.add_category, name='add-category'),

    path('translator/', views.home, name='translator'),
    path('search/', views.home, name='search'),
    path('add-word/', views.home, name='add-word'),
]