from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('ver-horas-trabajadas/', views.ver_horas_trabajadas, name='ver_horas_trabajadas'),
]
