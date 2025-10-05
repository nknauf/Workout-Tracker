from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date
import json
import requests
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from .models import (
    MuscleGroup, Equipment, Exercise, Workout, WorkoutExercise, 
    MealEntry, DailyLog, BaseExercise
)
from .forms import MealEntryForm
from .serializers import WorkoutSerializer, AIWorkoutCreateSerializer


@login_required
def home(request):
    """Dashboard showing today's activities and meal logging"""
    today = date.today()

    # Get or create today's log
    daily_log, created = DailyLog.objects.get_or_create(user=request.user, date=today)

    # Handle meal form submission
    if request.method == 'POST':
        form = MealEntryForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.date = today
            meal.save()

            daily_log.meals.add(meal)
            daily_log.total_calories += meal.calories
            daily_log.total_carbs += meal.carbs
            daily_log.total_fats += meal.fats
            daily_log.total_protein += meal.protein

            messages.success(request, f"Meal '{meal.name}' logged successfully!")
            return redirect('home')
    else:
        form = MealEntryForm()

    # Data for dashboard
    todays_workouts = daily_log.workouts.all()
    todays_meals = daily_log.meals.all().order_by('-created_at')

    context = {
        'form': form,
        'todays_workouts': todays_workouts,
        'workout_count': todays_workouts.count(),
        'todays_meals': todays_meals,
        'total_calories': daily_log.total_calories,
        'total_protein': daily_log.total_protein,
        'total_carbs': daily_log.total_carbs,
        'total_fats': daily_log.total_fats,
        'date': today,
    }
    return render(request, 'logger/home.html', context)


def create_workout(request):
    """For manually creating a workout without the help of n8n"""
    exercises_in_session = request.session.get("workout_exercises", {})
    workout_name = request.session.get("workout_name", "")

    if request.method == "POST":

        if "update_workout_name" in request.POST:
            workout_name = request.POST.get("workout_name", "").strip()
            request.session["workout_name"] = workout_name
            request.session.modified = True
            return JsonResponse({"status": "ok", "workout_name": workout_name})
        
        elif "add_exercise" in request.POST:
            exercise_id = request.POST.get("exercise_id")
            sets = request.POST.get("sets", 3)
            reps = request.POST.get("reps", 8)
            
            if exercise_id:
                exercises_in_session[exercise_id] = {
                    "sets": int(sets),
                    "reps": int(reps)
                }
                request.session["workout_exercises"] = exercises_in_session
                request.session.modified = True

        elif "update_exercise" in request.POST:
            exercise_id = request.POST.get("exercise_id")
            sets = request.POST.get("sets")
            reps = request.POST.get("reps")

            if exercise_id in exercises_in_session and sets and reps:
                exercises_in_session[exercise_id]["sets"] = int(sets)
                exercises_in_session[exercise_id]["reps"] = int(reps)
                request.session["workout_exercises"] = exercises_in_session
                request.session.modified = True
        
        elif "delete_exercise" in request.POST:
            exercise_id = request.POST.get("exercise_id")
            if exercise_id in exercises_in_session:
                del exercises_in_session[exercise_id]
                request.session["workout_exercises"] = exercises_in_session
                request.session.modified = True
        
        elif "cancel_workout" in request.POST:
            request.session.pop("workout_exercises", None)
            request.session.pop("workout_name", None)
            request.session.modified = True
            messages.info(request, "Workout creation cancelled.")
            return redirect("home")

        elif "save_workout" in request.POST:
            if exercises_in_session:
                try:
                    name = workout_name or f"Workout on {date.today()}"
                    workout = Workout.objects.create(
                        user=request.user,
                        name = name,
                        date = date.today()
                    )
                    for order, (ex_id, exercise_data) in enumerate(exercises_in_session.items()):
                        try:
                            exercise = Exercise.objects.get(id=int(ex_id))
                            WorkoutExercise.objects.create(
                                workout = workout,
                                user=request.user,
                                exercise = exercise,
                                sets = exercise_data["sets"],
                                reps = exercise_data["reps"],
                                order = order
                            )
                        except Exercise.DoesNotExist:
                            continue
                    daily_log, _ = DailyLog.objects.get_or_create(
                        user=request.user,
                        date = date.today()
                    )
                    daily_log.workouts.add(workout)
                    
                    request.session.pop("workout_exercises", None)
                    request.session.pop("workout_name", None)
                    request.session.modified = True

                    messages.success(request, f"Workout '{workout.name}' saved successfully!")
                    return redirect('home')
                
                except Exception as e:
                    messages.error(request, f"Error saving workout: {str(e)}")
            else:
                messages.warning(request, "No exercises selected.")
    
    muscle_filter = request.GET.getlist("muscle_group")
    equipment_filter = request.GET.getlist("equipment")

    exercise_qs = Exercise.objects.all()

    if muscle_filter:
        exercise_qs = exercise_qs.filter(base_exercise__primary_muscle_group_id__in=muscle_filter)
    if equipment_filter:
        exercise_qs = exercise_qs.filter(equipment_id__in=equipment_filter)

    exercise_qs = exercise_qs.exclude(id__in = exercises_in_session)
    
    available_exercises = {}
    for ex in exercise_qs.select_related("base_exercise"):
        base_ex = ex.base_exercise
        if base_ex not in available_exercises:
            available_exercises[base_ex] = []
        available_exercises[base_ex].append(ex)



    # Changed "selected_exercises" into a list, not a queryset or something. Keep it like this but know you need to 
    # update the rest of the view according to the new changes

    # selected_exercises = Exercise.objects.filter(id__in=exercises_in_session)
    selected_exercises = []
    for ex_id, data in exercises_in_session.items():
        try:
            ex = Exercise.objects.get(id=int(ex_id))
            ex.sets = data.get("sets", 3)
            ex.reps = data.get("reps", 8)
            selected_exercises.append(ex)
        except Exercise.DoesNotExist:
            continue


    context = {
        "workout_name": workout_name,
        "available_exercises": available_exercises,
        "selected_exercises": selected_exercises,
        "muscle_groups": MuscleGroup.objects.all(),
        "equipment": Equipment.objects.all(),
        "selected_muscle_groups": [int(m) for m in muscle_filter],
        "selected_equipment": [int(e) for e in equipment_filter],
    }
    return render(request, 'logger/create_workout.html', context)

@login_required
def delete_meal_log(request, meal_id):
    """Delete a meal from today's daily log."""
    meal = get_object_or_404(MealEntry, id=meal_id, user=request.user)

    if request.method == "POST":
        # Remove from daily log if it exists
        daily_log = DailyLog.objects.filter(user=request.user, date=date.today()).first()
        if daily_log and meal in daily_log.meals.all():
            daily_log.meals.remove(meal)

        meal.delete()
        messages.success(request, f"Meal '{meal.name}' deleted successfully!")

    return redirect("home")

@login_required
def ai_create_workout(request):
    """Where users will go to input their workout to the chatbot"""

    return render(request, "logger/ai_create_workout.html")

@login_required
def exercises(request):
    """
    Display all exercises grouped by primary muscle group, then by base exercise.
    """
    exercises_by_muscle = {}
    muscle_groups = MuscleGroup.objects.prefetch_related("primary_exercises__exercises") # fetches base_exercises related to each MG

    for muscle in muscle_groups:
        base_exercises_dict = {}
        for base_ex in muscle.primary_exercises.all(): # actually grabs base_exercises for MG, not primary MG
            exercises_list = list(base_ex.exercises.all())
            if exercises_list:
                base_exercises_dict[base_ex] = exercises_list
        exercises_by_muscle[muscle] = base_exercises_dict

    context = {
        "exercises_by_muscle": exercises_by_muscle
    }
    return render(request, "logger/exercises.html", context)


#  Simple API endpoints for n8n calls

# n8n webhook URL
N8N_WEBHOOK_URL = 'http://143.198.113.171:5678/webhook/workout-agent'

@api_view(['POST'])
def trigger_workout_agent(request):
    try:
        user_input = request.data.get('input', '')
        user_id = request.data.get('user_id', 1)

        if not user_input:
            return Response({"error": "Input is required"}, status=400)
        
        callback_url = request.build_absolute_uri('http://127.0.0.1:8000/api/create-workout-from-agent/')
        # http://127.0.0.1:8000/api/create-workout-from-agent/
        
        payload = {
            'input': user_input,
            'user_id': user_id,
            'callback_url': callback_url
        }
        
        # Test 3: Try the network request with detailed error info
        try:
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)  # Shorter timeout for testing
            
            return Response({
                'message': 'Network request test',
                'n8n_status': response.status_code,
                'n8n_response': response.text[:500],  # First 500 chars only
                'payload_sent': payload
            })
            
        except requests.exceptions.ConnectTimeout:
            return Response({'error': 'Connection timeout to n8n'}, status=500)
        except requests.exceptions.ConnectionError as e:
            return Response({'error': f'Connection error to n8n: {str(e)}'}, status=500)
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Request error: {str(e)}'}, status=500)
            
    except Exception as e:
        return Response({'error': f'Unexpected error: {str(e)}'}, status=500)

@csrf_exempt
@api_view(['POST'])
def create_workout_from_agent(request):
    """
    This endpoint receives the processed workout data back from n8n and creates the actual workout in the database
    """
    try:
        workout_data = request.data
        serializer = AIWorkoutCreateSerializer(data=workout_data)
        if serializer.is_valid():
            workout = serializer.save()
            daily_log, created = DailyLog.objects.get_or_create(
                user=workout.user, 
                date=workout.date
            )
            daily_log.workouts.add(workout)
            workout_serialized = WorkoutSerializer(workout)
            return Response({'message': 'Workout created successfully', 'workout': workout_serialized.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Failed to create workout', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_recent_workouts(request):
    """
    Helper endpoint to get recent workouts (for your chatbot to show)
    """
    user_id = request.GET.get('user_id', 1)
    try:
        user = User.objects.get(id=user_id)
        workouts = user.workout_set.all()[:5]  # Last 5 workouts
        serializer = WorkoutSerializer(workouts, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, 
                      status=status.HTTP_404_NOT_FOUND)