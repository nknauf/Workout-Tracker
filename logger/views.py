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
    MealEntry, DailyLog, SavedWorkout, SavedWorkoutExercise
)
from .forms import ExerciseForm, MealEntryForm  # Remove non-existent forms
from .serializers import WorkoutSerializer, AIWorkoutCreateSerializer


@login_required
def home(request):
    """Dashboard showing today's activities"""
    today = date.today()
    
    # Get or create today's log
    daily_log, created = DailyLog.objects.get_or_create(user=request.user, date=today)
    
    # Get today's workouts and meals
    todays_workouts = daily_log.workouts.all()
    todays_meals = daily_log.meals.all()
    
    context = {
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


@login_required
def create_exercise(request):
    """Create a new exercise"""
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save()
            messages.success(request, f"Exercise '{exercise.name}' created successfully!")
            return redirect('exercise_list')
    else:
        form = ExerciseForm()
    
    return render(request, 'logger/create_exercise.html', {'form': form})


@login_required
def exercise_list(request):
    """List all exercises with filtering"""
    exercises = Exercise.objects.all().select_related('primary_muscle_group', 'equipment')
    
    # Filter by muscle group
    muscle_filter = request.GET.get('muscle_group')
    if muscle_filter:
        exercises = exercises.filter(primary_muscle_group_id=muscle_filter)
    
    # Filter by equipment
    equipment_filter = request.GET.get('equipment')
    if equipment_filter:
        exercises = exercises.filter(equipment_id=equipment_filter)
    
    context = {
        'exercises': exercises.order_by('name'),
        'muscle_groups': MuscleGroup.objects.all(),
        'equipment': Equipment.objects.all(),
        'selected_muscle': muscle_filter,
        'selected_equipment': equipment_filter,
    }
    return render(request, 'logger/exercise_list.html', context)


@login_required
def create_workout(request):
    """Create a new workout using session storage"""
    
    # Get exercises already selected in session
    exercises_in_session = request.session.get('workout_exercises', [])
    workout_name = request.session.get('workout_name', '')
    
    if request.method == 'POST':
        # Handle different form actions
        if 'update_name' in request.POST:
            workout_name = request.POST.get('workout_name', '').strip()
            request.session['workout_name'] = workout_name
            request.session.modified = True
        
        elif 'load_saved_workout' in request.POST:
            saved_workout_id = request.POST.get('saved_workout_id')
            try:
                saved_workout = SavedWorkout.objects.get(id=saved_workout_id, user=request.user)
                
                # Load exercises from saved workout
                exercises_in_session = []
                for saved_ex in saved_workout.saved_exercises.all():
                    exercises_in_session.append(str(saved_ex.exercise.id))
                
                request.session['workout_exercises'] = exercises_in_session
                request.session['workout_name'] = saved_workout.name
                request.session.modified = True
                
                messages.success(request, f"Loaded saved workout: {saved_workout.name}")
                
            except SavedWorkout.DoesNotExist:
                messages.error(request, "Saved workout not found.")
        
        elif 'add_exercise' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id and exercise_id not in exercises_in_session:
                exercises_in_session.append(exercise_id)
                request.session['workout_exercises'] = exercises_in_session
                request.session.modified = True
        
        elif 'remove_exercise' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id in exercises_in_session:
                exercises_in_session.remove(exercise_id)
                request.session['workout_exercises'] = exercises_in_session
                request.session.modified = True
        
        elif 'cancel_workout' in request.POST:
            # Clear session and redirect
            request.session.pop('workout_exercises', None)
            request.session.pop('workout_name', None)
            request.session.modified = True
            messages.info(request, "Workout creation cancelled.")
            return redirect('home')
        
        elif 'save_workout' in request.POST:
            if exercises_in_session:
                try:
                    # Create the workout
                    name = workout_name or f"Workout - {date.today()}"
                    workout = Workout.objects.create(
                        user=request.user,
                        name=name,
                        date=date.today()
                    )
                    
                    # Add exercises with default values
                    for order, ex_id in enumerate(exercises_in_session):
                        try:
                            exercise = Exercise.objects.get(id=int(ex_id))
                            WorkoutExercise.objects.create(
                                workout=workout,
                                exercise=exercise,
                                sets=3,  # Default values
                                reps=10,
                                order=order
                            )
                        except Exercise.DoesNotExist:
                            continue
                    
                    # Add to today's log
                    daily_log, _ = DailyLog.objects.get_or_create(user=request.user, date=date.today())
                    daily_log.workouts.add(workout)
                    
                    # Clear session
                    request.session.pop('workout_exercises', None)
                    request.session.pop('workout_name', None)
                    request.session.modified = True
                    
                    messages.success(request, f"Workout '{workout.name}' saved successfully!")
                    return redirect('home')
                    
                except Exception as e:
                    messages.error(request, f"Error saving workout: {str(e)}")
            else:
                messages.warning(request, "No exercises selected.")
    
    # Get available exercises with filtering
    muscle_filter = request.GET.getlist('muscle_group')
    equipment_filter = request.GET.getlist('equipment')
    
    available_exercises = Exercise.objects.all()
    if muscle_filter:
        available_exercises = available_exercises.filter(primary_muscle_group_id__in=muscle_filter)
    if equipment_filter:
        available_exercises = available_exercises.filter(equipment_id__in=equipment_filter)
    
    # Exclude already selected exercises
    available_exercises = available_exercises.exclude(id__in=exercises_in_session)
    selected_exercises = Exercise.objects.filter(id__in=exercises_in_session)
    
    # Get user's saved workouts
    saved_workouts = SavedWorkout.objects.filter(user=request.user).order_by('-is_favorite', '-last_used')[:10]
    
    context = {
        'workout_name': workout_name,
        'available_exercises': available_exercises.select_related('primary_muscle_group', 'equipment'),
        'selected_exercises': selected_exercises,
        'muscle_groups': MuscleGroup.objects.all(),
        'equipment': Equipment.objects.all(),
        'selected_muscles': [int(m) for m in muscle_filter],
        'selected_equipment': [int(e) for e in equipment_filter],
        'saved_workouts': saved_workouts,
    }
    return render(request, 'logger/create_workout.html', context)


@login_required
def log_meal_entry(request):
    """Log a meal entry for today"""
    daily_log, created = DailyLog.objects.get_or_create(user=request.user, date=date.today())
    
    if request.method == 'POST':
        form = MealEntryForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.date = date.today()
            meal.save()
            
            # Add to daily log
            daily_log.meals.add(meal)
            
            # Update daily totals
            update_daily_totals(daily_log)
            
            messages.success(request, f"Meal '{meal.name}' logged successfully!")
            return redirect('log_meal_entry')
    else:
        form = MealEntryForm()
    
    # Get today's meals
    todays_meals = daily_log.meals.all().order_by('-created_at')
    
    context = {
        'form': form,
        'meals': todays_meals,
        'total_calories': daily_log.total_calories,
        'total_protein': daily_log.total_protein,
        'total_carbs': daily_log.total_carbs,
        'total_fats': daily_log.total_fats,
    }
    return render(request, 'logger/log_meal_entry.html', context)


@login_required
def calendar(request):
    """View daily logs by date"""
    selected_date = request.GET.get('date', date.today().isoformat())
    parsed_date = parse_date(selected_date) or date.today()
    
    # Get daily log for selected date
    daily_log, _ = DailyLog.objects.get_or_create(user=request.user, date=parsed_date)
    
    # Get workouts with exercise details
    workouts = daily_log.workouts.prefetch_related('workoutexercise_set__exercise')
    workouts_with_details = []
    
    for workout in workouts:
        workout_exercises = workout.workoutexercise_set.all().order_by('order')
        workouts_with_details.append({
            'workout': workout,
            'exercises': workout_exercises,
            'exercise_count': workout_exercises.count()
        })
    
    # Get meals
    meals = daily_log.meals.all().order_by('-created_at')
    
    context = {
        'selected_date': selected_date,
        'date': parsed_date,
        'daily_log': daily_log,
        'workouts_with_details': workouts_with_details,
        'meals': meals,
        'is_today': parsed_date == date.today()
    }
    return render(request, 'logger/calendar.html', context)


@login_required
def saved_workouts(request):
    """Manage saved workout templates"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_from_workout':
            workout_id = request.POST.get('workout_id')
            try:
                workout = Workout.objects.get(id=workout_id, user=request.user)
                saved_name = request.POST.get('name', workout.name)
                
                # Create saved workout
                saved_workout = SavedWorkout.objects.create(
                    user=request.user,
                    name=saved_name,
                    description=f"Created from workout on {workout.date}"
                )
                
                # Copy exercises
                for workout_ex in workout.workoutexercise_set.all():
                    SavedWorkoutExercise.objects.create(
                        saved_workout=saved_workout,
                        exercise=workout_ex.exercise,
                        default_sets=workout_ex.sets,
                        default_reps=workout_ex.reps,
                        default_weight=workout_ex.weight,
                        order=workout_ex.order
                    )
                
                messages.success(request, f"Saved workout '{saved_name}' created!")
                
            except Workout.DoesNotExist:
                messages.error(request, "Workout not found.")
        
        elif action == 'delete':
            saved_workout_id = request.POST.get('saved_workout_id')
            try:
                saved_workout = SavedWorkout.objects.get(id=saved_workout_id, user=request.user)
                saved_workout.delete()
                messages.success(request, "Saved workout deleted.")
            except SavedWorkout.DoesNotExist:
                messages.error(request, "Saved workout not found.")
    
    # Get user's saved workouts and recent workouts
    saved_workouts = SavedWorkout.objects.filter(user=request.user).order_by('-is_favorite', '-last_used')
    recent_workouts = Workout.objects.filter(user=request.user).order_by('-date')[:10]
    
    context = {
        'saved_workouts': saved_workouts,
        'recent_workouts': recent_workouts,
    }
    return render(request, 'logger/saved_workouts.html', context)


@login_required
def delete_workout(request, workout_id):
    """Delete a workout"""
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        workout_name = workout.name
        workout.delete()
        messages.success(request, f"Workout '{workout_name}' deleted successfully!")
    return redirect('calendar')


@login_required
def delete_meal(request, meal_id):
    """Delete a meal entry"""
    meal = get_object_or_404(MealEntry, id=meal_id, user=request.user)
    if request.method == 'POST':
        meal_name = meal.name
        meal_date = meal.date
        meal.delete()
        
        # Update daily totals
        try:
            daily_log = DailyLog.objects.get(user=request.user, date=meal_date)
            update_daily_totals(daily_log)
        except DailyLog.DoesNotExist:
            pass
        
        messages.success(request, f"Meal '{meal_name}' deleted successfully!")
    return redirect('calendar')


# Utility functions

def update_daily_totals(daily_log):
    """Update the cached totals for a daily log"""
    meals = daily_log.meals.all()
    
    daily_log.total_calories = sum(meal.calories for meal in meals)
    daily_log.total_protein = sum(meal.protein for meal in meals)
    daily_log.total_carbs = sum(meal.carbs for meal in meals)
    daily_log.total_fats = sum(meal.fats for meal in meals)
    daily_log.save()


#  Simple API endpoints for n8n calls

# n8n webhook URL
N8N_WEBHOOK_URL = 'http://143.198.113.171:5678/webhook/workout-agent'

# @api_view(['POST'])
# def trigger_workout_agent(request):
#     """This enpoint receives a workout request and sends it to n8n
#     Call this from the chatbot"""
#     try:
#         user_input = request.data.get('input', '')
#         user_id = request.data.get('user_id', 1) # Default to user 1

#         if not user_input:
#             return Response({"error": "Input is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         payload = {
#             'input': user_input,
#             'user_id': user_id,
#             'callback_url': request.build_absolute_uri('/api/create-workout-from-agent/')
#         }
#         response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=40)

#         if response.status_code == 200:
#             return Response({'message': 'Workout request sent to agent', 'status': 'processing'})
#         else:
#             return Response({'error': 'Failed to trigger workout agent', 'details': response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     except Exception as e:
#         return Response({'error': 'Unexpected error','details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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