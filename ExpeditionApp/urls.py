from django.urls import path
from .views import home, welcome, liste_expeditions, detailsExpedition, deleteExpedition

urlpatterns = [
    path('home/', home, name='home'),
    path('welcome/<str:name>/', welcome, name='welcome'),
    path('list/', liste_expeditions, name='list'),
    path('details/<int:pk>/', detailsExpedition, name='details'),
    path('delete/<int:pk>/', deleteExpedition, name='delete'),
]