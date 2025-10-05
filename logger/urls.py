from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('create-workout/', views.create_workout, name='create_workout'),
    path('ai-create-workout/', views.ai_create_workout, name='ai_create_workout'),
    path('exercises/', views.exercises, name="exercises"),
    path("delete-meal/<int:meal_id>/", views.delete_meal_log, name="delete_meal_log"),
    
    # API endpoints for n8n integration
    path('api/trigger-workout-agent/', views.trigger_workout_agent, name='trigger_workout_agent'),
    path('api/create-wrkout-from-agent/', views.create_workout_from_agent, name='create_workout_from_agent'),
    path('api/recent-workouts/', views.get_recent_workouts, name='get_recent_workouts'),
]