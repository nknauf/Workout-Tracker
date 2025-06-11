from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('create-exercise/', views.create_exercise, name='create_exercise'),
    path('create-workout/', views.create_workout, name='create_workout'),
    path('log-calories/', views.log_calories, name='log_calories'),
    path('calendar/', views.calendar, name='calendar'),
    path('edit-workouts/<int:workout_id>/', views.edit_workout, name='edit_workout'),
    path('delete-workout/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    path('delete-meal-log/<int:meal_id>/', views.delete_meal_log, name='delete_meal_log'),
    path('edit-meal-log/<int:meal_id>/', views.edit_meal_log, name='edit_meal_log'),
    path('select-existing-workout/', views.select_existing_workout, name='select_existing_workout'),
    path('select-existing-meal/', views.select_existing_meal, name='select_existing_meal'),
]