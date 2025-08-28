from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    
    # Exercise management
    path('create-exercise/', views.create_exercise, name='create_exercise'),
    path('exercise-list/', views.exercise_list, name='exercise_list'),
    
    # Workout management
    path('create-workout/', views.create_workout, name='create_workout'),
    path('saved-workouts/', views.saved_workouts, name='saved_workouts'),
    path('delete-workout/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    
    # Meal management
    path('log-meal-entry/', views.log_meal_entry, name='log_meal_entry'),
    path('delete-meal/<int:meal_id>/', views.delete_meal, name='delete_meal'),
    
    # Calendar and daily logs
    path('calendar/', views.calendar, name='calendar'),
    
    # API endpoints for n8n integration
    path('api/trigger-workout-agent/', views.trigger_workout_agent, name='trigger_workout_agent'),
    path('api/create-wrkout-from-agent/', views.create_workout_from_agent, name='create_workout_from_agent'),
    path('api/recent-workouts/', views.get_recent_workouts, name='get_recent_workouts'),
]