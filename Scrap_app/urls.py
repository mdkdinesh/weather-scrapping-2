from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('dataset/', views.dataset, name='dataset'),
    path('getcsv/', views.getcsv, name='getcsv'),
    ]
