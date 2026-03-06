from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),

    path('dictionary/', views.dictionary, name='dictionary'),
    path('dictionary/category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('dictionary/text/<slug:slug>/', views.text_lemma_detail, name='text_lemma_detail'),
    path('dictionary/gesture/<int:pk>/', views.gesture_lemma_detail, name='gesture_lemma_detail'),

    path('personal/', views.personal_dict, name='personal_dict'),
    path('personal/add/<str:lemma_type>/<int:lemma_id>/', views.add_to_personal, name='add_to_personal'),

    path('contribute/', views.contribute, name='contribute'),
    path('contribute/annotation/', views.annotation, name='annotation'),

    path('moderation/', views.moderation, name='moderation'),
]