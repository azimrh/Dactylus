from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),

    path('dictionary/', views.dictionary, name='dictionary'),
    path('dictionary/category/<slug:slug>/', views.category, name='category'),
    path('dictionary/text/<slug:slug>/', views.text_lemma, name='text_lemma'),
    path('dictionary/gesture/<int:pk>/', views.gesture_lemma, name='gesture_lemma'),

    path('translator/', views.index, name='translator'),
    path('search/', views.index, name='search'),
    path('add-word/', views.index, name='add-word'),
    path('add-category/', views.index, name='add-category'),

    path('my-dictionary/', views.personal_dict, name='my-dictionary'),
    path('my-dictionary/add/<str:lemma_type>/<int:lemma_id>/', views.add_to_personal, name='add_to_personal'),

    path('moderation/', views.moderation, name='moderation'),
]