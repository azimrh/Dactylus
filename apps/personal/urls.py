from django.urls import path
from . import views

urlpatterns = [
    path('personal/', views.page_personal, name='personal')
]