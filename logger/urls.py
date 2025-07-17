from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-exercise/', views.create_exercise, name='create_exercise'),
    path('create-workout/', views.create_workout, name='create_workout'),
    path('log-meal-entry/', views.log_meal_entry, name='log_meal_entry'),
    path('calendar/', views.calendar, name='calendar'),
    
    # Workout management
    path('edit-workout/<int:workout_id>/', views.edit_workout, name='edit_workout'),
    path('delete-workout/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    path('log-workout-entry/', views.log_workout_entry, name='log_workout_entry'),
    path('select-existing-workout/', views.select_existing_workout, name='select_existing_workout'),
    
    # Meal management
    path('edit-meal-log/<int:meal_id>/', views.edit_meal_log, name='edit_meal_log'),
    path('delete-meal-log/<int:meal_id>/', views.delete_meal_log, name='delete_meal_log'),
    path('select-existing-meal/', views.select_existing_meal, name='select_existing_meal'),
    
    # Exercise management
    path('exercise-list/', views.exercise_list, name='exercise_list'),
    path('edit-exercise/<int:exercise_id>/', views.edit_exercise, name='edit_exercise'),
    path('delete-exercise/<int:exercise_id>/', views.delete_exercise, name='delete_exercise'),
]