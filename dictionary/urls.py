from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),

    path('dictionary/', views.dictionary, name='dictionary'),
    path('dictionary/category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('dictionary/text/<slug:slug>/', views.text_lemma_detail, name='text_lemma_detail'),
    path('dictionary/gesture/<int:pk>/', views.gesture_lemma_detail, name='gesture_lemma_detail'),

    path('meaning/<int:pk>/', views.meaning_detail, name='meaning_detail'),

    path('translator/', views.translator, name='translator'),

    path('personal/', views.personal_dict, name='personal_dict'),
    path('personal/add/<str:lemma_type>/<int:lemma_id>/', views.add_to_personal, name='add_to_personal'),

    path('contribute/', views.contribute, name='contribute'),
    path('contribute/invariants/', views.invariants, name='invariants'),
    path('contribute/invariants/submit/', views.submit_invariant, name='submit_invariant'),
    path('contribute/homonyms/', views.homonym_disambiguation, name='homonym_disambiguation'),
    path('contribute/homonyms/submit/', views.submit_disambiguation, name='submit_disambiguation'),
    path('contribute/annotation/', views.annotation, name='annotation'),
    path('contribute/explanation/add/', views.add_explanation, name='add_explanation'),
    path('contribute/example/add/', views.add_example, name='add_example'),

    path('moderation/', views.moderation, name='moderation'),
    path('moderation/<str:lemma_type>/<int:lemma_id>/<str:action>/', views.moderate_lemma, name='moderate_lemma'),
]