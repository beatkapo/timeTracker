from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('week/', views.week, name='week'),
]
