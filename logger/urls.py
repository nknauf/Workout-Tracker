from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('create-exercise/', views.create_exercise, name='create_exercise'),
    path('create-workout/', views.create_workout, name='create_workout'),
    path('log-calories/', views.log_calories, name='log_calories'),
]