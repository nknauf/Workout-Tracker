from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-exercise/', views.create_exercise, name='create_exercise'),
    path('create-workout/', views.create_workout, name='create_workout'),
    path('log-meal-entry/', views.log_meal_entry, name='log_meal_entry'),
    path('calendar/', views.calendar, name='calendar'),

    path('conversational-input/', views.conversational_input, name='conversational_input'),
    path('confirm-nlp-workout/', views.confirm_nlp_workout, name='confirm_nlp_workout'),
    path('api/nlp/process/', views.api_nlp_process, name='api_nlp_process'),
]