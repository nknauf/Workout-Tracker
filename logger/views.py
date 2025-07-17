from django.shortcuts import render, redirect, get_object_or_404
from .forms import ExerciseForm, WorkoutForm, MealEntryForm, ConversationalInputForm, ConfirmationForm, BaseExerciseForm, DropSetExerciseForm, SuperSetExerciseForm
from .models import (
    Workout, Exercise, Equipment, Muscle, MealEntry, DailyLog, 
    WorkoutTemplate, MealTemplate, BaseMuscle, BaseExercise, 
    DropSetExercise, DropSetRound, SuperSetExercise, SuperSetExerciseItem,
    WorkoutExerciseItem
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from django.db.models import Prefetch
from django.utils.dateparse import parse_date
from django.contrib.contenttypes.models import ContentType
from .nlp_processor import NLPProcessor
import json

@login_required
def home(request):
    today = date.today()
    log, created = DailyLog.objects.get_or_create(user=request.user, date=today) # Creates a log for today if it doesn't exist
    meal_entries = log.meals.filter(user=request.user) if log else []
    total_calories = sum(entry.calories for entry in meal_entries)
    total_protein = sum(entry.protein for entry in meal_entries)
    total_carbs = sum(entry.carbs for entry in meal_entries)
    total_fats = sum(entry.fats for entry in meal_entries)

    return render(request, 'logger/home.html' , {
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fats': total_fats,
    })


@login_required
def create_exercise(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save()
            form.save_m2m()
            messages.success(request, "Exercise created successfully!")
            return redirect('exercise_list')
    else:
        form = ExerciseForm()
    return render(request, 'logger/create_exercise.html', {'form': form})

@login_required
def create_workout(request):
    # Initialize session data if not present
    # if 'workout_exercises' not in request.session:
    #     request.session('workout_exercises') = []
    # if 'workout_drop_sets' not in request.session:
    #     request.session('workout_drop_sets') = []
    # if 'workout_super_sets' not in request.session:
    #     request.session('workout_super_sets') = []

    # get current session data
    exercises_in_session = request.session.get('workout_exercises', [])
    drop_sets_in_session = request.session.get('workout_drop_sets', [])
    super_sets_in_session = request.session.get('workout_super_sets', [])

    # Handle workout name
    if request.method == 'POST':
        workout_name = request.POST.get('workout_name', '').strip()
    else:
        workout_name = request.GET.get('workout_name', '').strip()

    if request.method == 'POST':
        workout_name = request.POST.get('workout_name', '').strip()
    else:
        workout_name = request.GET.get('workout_name', '').strip()

    # Handle exercise selection to add to session
    if request.method == 'POST':

        # Update workout name
        if 'update_name' in request.POST:
            request.session['workout_name'] = workout_name
            request.session.modified = True
        
        # Add exercise to exercises in session
        if 'add_exercise' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id and exercise_id not in exercises_in_session:
                exercises_in_session.append(exercise_id)
                request.session['workout_exercises'] = exercises_in_session
                request.session.modified = True
            
        # Remove exercise from exercises in session
        elif 'remove_exercise' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id in exercises_in_session:
                exercises_in_session.remove(exercise_id)
                request.session['workout_exercises'] = exercises_in_session
                request.session.modified = True

        # Convert exercise to drop set
        elif 'make_dropset' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id in exercises_in_session:
                exercises_in_session.remove(exercise_id)
                if exercise_id not in drop_sets_in_session:
                    drop_sets_in_session.append(exercise_id)
                request.session['workout_exercises'] = exercises_in_session
                request.session['workout_drop_sets'] = drop_sets_in_session
                request.session.modified = True

        # Convert exercise to super set
        elif 'make_superset' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id in exercises_in_session:
                # Remove from regular exercises
                exercises_in_session.remove(exercise_id)
                # Add to super sets if not already there
                if exercise_id not in super_sets_in_session:
                    super_sets_in_session.append(exercise_id)
                request.session['workout_exercises'] = exercises_in_session
                request.session['workout_super_sets'] = super_sets_in_session
                request.session.modified = True
                
        # Start superset creation mode
        elif 'start_superset' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id in exercises_in_session:
                request.session['superset_selection_mode'] = True
                request.session['superset_candidates'] = [exercise_id]
                request.session.modified = True
                
        # Add exercise to superset candidates
        elif 'add_to_superset' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            candidates = request.session.get('superset_candidates', [])
            if exercise_id not in candidates:
                candidates.append(exercise_id)
                request.session['superset_candidates'] = candidates
                request.session.modified = True
                
        # Remove exercise from superset candidates
        elif 'remove_from_superset' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            candidates = request.session.get('superset_candidates', [])
            if exercise_id in candidates:
                candidates.remove(exercise_id)
                request.session['superset_candidates'] = candidates
                request.session.modified = True
                
        # Create superset from candidates
        elif 'create_superset' in request.POST:
            candidates = request.session.get('superset_candidates', [])
            if len(candidates) >= 2:  # Need at least 2 exercises for superset
                # Remove candidates from regular exercises
                for candidate_id in candidates:
                    if candidate_id in exercises_in_session:
                        exercises_in_session.remove(candidate_id)
                    # Add to superset list
                    if candidate_id not in super_sets_in_session:
                        super_sets_in_session.append(candidate_id)
                
                request.session['workout_exercises'] = exercises_in_session
                request.session['workout_super_sets'] = super_sets_in_session
                request.session['superset_selection_mode'] = False
                request.session['superset_candidates'] = []
                request.session.modified = True
                messages.success(request, f"Superset created with {len(candidates)} exercises!")
            else:
                messages.error(request, "You need at least 2 exercises to create a superset.")
                
        # Cancel superset creation
        elif 'cancel_superset' in request.POST:
            request.session['superset_selection_mode'] = False
            request.session['superset_candidates'] = []
            request.session.modified = True
                
        # Remove drop set
        elif 'remove_dropset' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id in drop_sets_in_session:
                drop_sets_in_session.remove(exercise_id)
                request.session['workout_drop_sets'] = drop_sets_in_session
                request.session.modified = True
                
        elif 'remove_superset' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id in super_sets_in_session:
                super_sets_in_session.remove(exercise_id)
                request.session['workout_super_sets'] = super_sets_in_session
                request.session.modified = True

        # Convert drop set back to regular exercise
        elif 'dropset_to_exercise' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id in drop_sets_in_session:
                drop_sets_in_session.remove(exercise_id)
                if exercise_id not in exercises_in_session:
                    exercises_in_session.append(exercise_id)
                request.session['workout_drop_sets'] = drop_sets_in_session
                request.session['workout_exercises'] = exercises_in_session
                request.session.modified = True
                
        # Convert super set back to regular exercise
        elif 'superset_to_exercise' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id in super_sets_in_session:
                super_sets_in_session.remove(exercise_id)
                if exercise_id not in exercises_in_session:
                    exercises_in_session.append(exercise_id)
                request.session['workout_super_sets'] = super_sets_in_session
                request.session['workout_exercises'] = exercises_in_session
                request.session.modified = True
                
        elif 'save_workout' in request.POST:
            if exercises_in_session or drop_sets_in_session or super_sets_in_session:
                log, _ = DailyLog.objects.get_or_create(user=request.user, date=date.today())
                name = workout_name if workout_name else "Workout for " + date.today().strftime("%Y-%m-%d")
                workout = Workout.objects.create(user=request.user, name=name)
                
                order = 0
                # Add regular exercises
                for ex_id in exercises_in_session:
                    exercise = Exercise.objects.get(id=int(ex_id))
                    WorkoutExerciseItem.objects.create(
                        workout=workout,
                        content_type=ContentType.objects.get_for_model(Exercise),
                        object_id=exercise.id,
                        order=order
                    )
                    order += 1
                # Add drop set to exercises
                for ex_id in drop_sets_in_session:
                    exercise = Exercise.objects.get(id=int(ex_id))
                    drop_set, created = DropSetExercise.objects.get_or_create(
                        base_exercise = exercise,
                        user=request.user,
                        defaults={'is_active': True}
                    )
                    WorkoutExerciseItem.objects.create(
                        workout=workout,
                        content_type=ContentType.objects.get_for_model(DropSetExercise),
                        object_id=drop_set.id,
                        order=order
                    )
                    order += 1
                # Add super set to exercises
                for ex_id in super_sets_in_session:
                    exercise = Exercise.objects.get(id=int(ex_id))
                    super_set, created = SuperSetExercise.objects.get_or_create(
                        base_exercise=exercise,
                        user=request.user,
                        defaults={'is_active': True}
                    )
                    WorkoutExerciseItem.objects.create(
                        workout=workout,
                        content_type=ContentType.objects.get_for_model(SuperSetExercise),
                        object_id=super_set.id,
                        order=order
                    )
                    order += 1
                log.workouts.add(workout)

            
                # Clear session
                request.session['workout_exercises'] = []
                request.session['workout_drop_sets'] = []
                request.session['workout_super_sets'] = []
                request.session.modified = True
                messages.success(request, "Workout saved!")
                return redirect('home')
            else:
                messages.error(request, "You must add at least one exercise to the workout.")

    # Fetching filters from the request
    selected_muscles = request.GET.getlist('muscle_group')
    equipment_filter = request.GET.getlist('equipment')

    exercises = Exercise.objects.all()
    drop_sets = DropSetExercise.objects.filter(user=request.user, is_active=True)
    super_sets = SuperSetExercise.objects.filter(user=request.user, is_active=True)
    
    available_exercises = exercises
    if equipment_filter:
        available_exercises = available_exercises.filter(equipment__id__in=equipment_filter)
    if selected_muscles:
        available_exercises = available_exercises.filter(muscle_group__id__in=selected_muscles)

    # Remove already selected exercsies from available list
    all_selected_ids = exercises_in_session + drop_sets_in_session + super_sets_in_session
    available_exercises = available_exercises.exclude(id__in=all_selected_ids)
    
    selected_exercises = Exercise.objects.filter(id__in=exercises_in_session)
    selected_drop_sets = DropSetExercise.objects.filter(id__in=drop_sets_in_session)
    selected_super_sets = SuperSetExercise.objects.filter(id__in=super_sets_in_session)

    context = {
        'workout_name': workout_name,
        'available_exercises': available_exercises.distinct(),
        'muscles': Muscle.objects.all(),
        'equipment': Equipment.objects.all(),
        'selected_muscles': [int(m) for m in selected_muscles],
        'selected_equipment': [int(e) for e in equipment_filter],
        'selected_exercises': selected_exercises,
        'selected_drop_sets': selected_drop_sets,
        'selected_super_sets': selected_super_sets,
    }
    return render(request, 'logger/create_workout.html', context)

@login_required
def log_meal_entry(request):
    log, created = DailyLog.objects.get_or_create(user=request.user, date=date.today())
    if request.method == 'POST':
        form = MealEntryForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.save()
            log.meals.add(meal)
            messages.success(request, f"Meal '{meal.name}' logged for today!")
            return redirect('log_meal_entry')
    else:
        form = MealEntryForm()

    entries = log.meals.filter(user=request.user).order_by('-created_at')
    total_calories = sum(entry.calories for entry in entries)
    total_protein = sum(entry.protein for entry in entries)
    total_carbs = sum(entry.carbs for entry in entries)
    total_fats = sum(entry.fats for entry in entries)
    
    context = {
        'form': form,
        'entries': entries,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fats': total_fats,
    }
    return render(request, 'logger/log_calories.html', context)

@login_required
def calendar(request):
    selected_date = request.GET.get('date', date.today().isoformat())
    parsed_date = parse_date(selected_date) or date.today()

    daily_log, _ = DailyLog.objects.get_or_create(user=request.user, date=parsed_date)

    meals = daily_log.meals.filter(user=request.user) if daily_log else []
    total_calories = sum(meal.calories for meal in meals)
    total_protein = sum(meal.protein for meal in meals)

    workouts = daily_log.workouts.all().prefetch_related('items')
    if not workouts:
        messages.info(request, "No workouts found for this date.")

    return render(request, 'logger/calendar.html', {
        'workouts': workouts,
        'selected_date': selected_date,
        'date': parsed_date,
        'meals': meals,
        'total_calories': total_calories,
        'total_protein': total_protein,
    })

@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)

    if request.method == 'GET' and (not request.session.get('workout_exercises')):
        # Load existing workout items into session
        exercises_in_session = []
        drop_sets_in_session = []
        super_sets_in_session = []
        
        for item in workout.items.all():
            if item.content_type.model == 'exercise':
                exercises_in_session.append(str(item.object_id))
            elif item.content_type.model == 'dropsetexercise':
                drop_sets_in_session.append(str(item.object_id))
            elif item.content_type.model == 'supersetexercise':
                super_sets_in_session.append(str(item.object_id))
        
        request.session['workout_exercises'] = exercises_in_session
        request.session['workout_drop_sets'] = drop_sets_in_session
        request.session['workout_super_sets'] = super_sets_in_session

    if request.method == 'POST':
        workout_name = request.POST.get('workout_name', workout.name)

        if 'add_exercise_to_workout' in request.POST:
            selected_ids = request.POST.getlist('exercise_ids')
            for ex_id in selected_ids:
                if ex_id not in request.session['workout_exercises']:
                    request.session['workout_exercises'].append(ex_id)
            request.session.modified = True
            
        elif 'add_dropset_to_workout' in request.POST:
            selected_ids = request.POST.getlist('dropset_ids')
            for ds_id in selected_ids:
                if ds_id not in request.session['workout_drop_sets']:
                    request.session['workout_drop_sets'].append(ds_id)
            request.session.modified = True
            
        elif 'add_superset_to_workout' in request.POST:
            selected_ids = request.POST.getlist('superset_ids')
            for ss_id in selected_ids:
                if ss_id not in request.session['workout_super_sets']:
                    request.session['workout_super_sets'].append(ss_id)
            request.session.modified = True
            
        elif 'save_workout' in request.POST:
            workout.name = workout_name
            workout.save()
            
            # Clear existing items and recreate
            workout.items.all().delete()
            
            order = 0
            # Add exercises
            for ex_id in request.session['workout_exercises']:
                exercise = Exercise.objects.get(id=int(ex_id))
                WorkoutExerciseItem.objects.create(
                    workout=workout,
                    content_type=ContentType.objects.get_for_model(Exercise),
                    object_id=exercise.id,
                    order=order
                )
                order += 1
            
            # Add drop sets
            for ds_id in request.session['workout_drop_sets']:
                drop_set = DropSetExercise.objects.get(id=int(ds_id))
                WorkoutExerciseItem.objects.create(
                    workout=workout,
                    content_type=ContentType.objects.get_for_model(DropSetExercise),
                    object_id=drop_set.id,
                    order=order
                )
                order += 1
            
            # Add super sets
            for ss_id in request.session['workout_super_sets']:
                super_set = SuperSetExercise.objects.get(id=int(ss_id))
                WorkoutExerciseItem.objects.create(
                    workout=workout,
                    content_type=ContentType.objects.get_for_model(SuperSetExercise),
                    object_id=super_set.id,
                    order=order
                )
                order += 1
            
            messages.success(request, "Workout updated successfully!")
            request.session['workout_exercises'] = []
            request.session['workout_drop_sets'] = []
            request.session['workout_super_sets'] = []
            return redirect('calendar')
            
        elif 'remove_exercise' in request.POST:
            to_remove = request.POST.get('remove_exercise')
            if to_remove in request.session['workout_exercises']:
                request.session['workout_exercises'].remove(to_remove)
                request.session.modified = True
                
        elif 'remove_dropset' in request.POST:
            to_remove = request.POST.get('remove_dropset')
            if to_remove in request.session['workout_drop_sets']:
                request.session['workout_drop_sets'].remove(to_remove)
                request.session.modified = True
                
        elif 'remove_superset' in request.POST:
            to_remove = request.POST.get('remove_superset')
            if to_remove in request.session['workout_super_sets']:
                request.session['workout_super_sets'].remove(to_remove)
                request.session.modified = True

    muscle_ids = request.GET.getlist('muscle_group')
    equipment_filter = request.GET.getlist('equipment')

    exercises = Exercise.objects.all()
    drop_sets = DropSetExercise.objects.filter(user=request.user, is_active=True)
    super_sets = SuperSetExercise.objects.filter(user=request.user, is_active=True)
    
    if equipment_filter:
        exercises = exercises.filter(equipment__id__in=equipment_filter)
    if muscle_ids:
        exercises = exercises.filter(muscle_group__id__in=muscle_ids)

    context = {
        'workout_name': workout.name,
        'available_exercises': exercises,
        'available_drop_sets': drop_sets,
        'available_super_sets': super_sets,
        'selected_exercises': Exercise.objects.filter(id__in=request.session.get('workout_exercises', [])),
        'selected_drop_sets': DropSetExercise.objects.filter(id__in=request.session.get('workout_drop_sets', [])),
        'selected_super_sets': SuperSetExercise.objects.filter(id__in=request.session.get('workout_super_sets', [])),
        'muscles': Muscle.objects.all(),
        'equipment': Equipment.objects.all(),
        'selected_muscles': [int(m) for m in muscle_ids],
        'selected_equipment': [int(e) for e in equipment_filter],
        'edit_mode': True,
    }
    return render(request, 'logger/create_workout.html', context)

@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        workout.delete()
        messages.success(request, "Workout deleted successfully!")
    return redirect('calendar')

@login_required
def delete_meal_log(request, meal_id):
    meal = get_object_or_404(MealEntry, id=meal_id, user=request.user)
    if request.method == 'POST':
        meal.delete()
        messages.success(request, "Meal log deleted successfully!")
    return redirect('home')

@login_required
def edit_meal_log(request, meal_id):
    meal = get_object_or_404(MealEntry, id=meal_id, user=request.user)
    if request.method == 'POST':
        form = MealEntryForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()
            messages.success(request, "Meal log updated successfully!")
            return redirect('home')
    else:
        form = MealEntryForm(instance=meal)
    return render(request, 'logger/edit_meal_log.html', {'form': form, 'meal': meal})

@login_required
def log_workout_entry(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            return redirect('create_workout')
        elif action == 'existing':
            return redirect('select_existing_workout')
    return render(request, 'logger/log_workout_entry.html', {})

@login_required
def select_existing_workout(request):
    workouts = Workout.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        workout_id = request.POST.get('workout_id')
        action = request.POST.get('log_existing') or request.POST.get('edit_existing')

        if workout_id:
            original_workout = get_object_or_404(Workout, id=workout_id, user=request.user)
            if 'log_existing' in request.POST:
                # Create a copy of the workout for today
                workout = Workout.objects.create(
                    name=f"{original_workout.name} (Copy)",
                    user=request.user
                )
                
                # Copy all items from original workout
                for item in original_workout.items.all():
                    WorkoutExerciseItem.objects.create(
                        workout=workout,
                        content_type=item.content_type,
                        object_id=item.object_id,
                        order=item.order
                    )
                
                log, _ = DailyLog.objects.get_or_create(user=request.user, date=date.today())
                log.workouts.add(workout)
                messages.success(request, "Workout successfully logged.")
                return redirect('home')
            elif 'edit_existing' in request.POST:
                return redirect('edit_workout', workout_id=workout.id)
    return render(request, 'logger/select_existing_workout.html', {'workouts': workouts})

@login_required
def select_existing_meal(request):
    meals = MealEntry.objects.filter(user=request.user, is_template=True).order_by('-created_at')
    if request.method == 'POST':
        meal_id = request.POST.get('meal_id')
        meal = get_object_or_404(MealEntry, id=meal_id, user=request.user)

        if meal_id:
            log, created = DailyLog.objects.get_or_create(user=request.user, date=date.today())

            if 'log_existing' in request.POST:
                # Create a copy of the meal for today
                new_meal = MealEntry.objects.create(
                    name=meal.name,
                    calories=meal.calories,
                    protein=meal.protein,
                    carbs=meal.carbs,
                    fats=meal.fats,
                    user=request.user,
                    is_template=False
                )
                log.meals.add(new_meal)
                messages.success(request, "Meal successfully logged")
                return redirect('home')

            elif 'edit_existing' in request.POST:
                return redirect('edit_meal_log', meal_id=meal.id)
    return render(request, 'logger/select_existing_meal.html', {'meals': meals})

# Additional views for exercise management
@login_required
def exercise_list(request):
    exercises = Exercise.objects.all().order_by('name')
    base_exercises = BaseExercise.objects.all().order_by('name')
    context = {
        'exercises': exercises,
        'base_exercises': base_exercises,
    }
    return render(request, 'logger/exercise_list.html', context)

@login_required
def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, "Exercise updated successfully!")
            return redirect('exercise_list')
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, 'logger/edit_exercise.html', {'form': form, 'exercise': exercise})

@login_required
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
    if request.method == 'POST':
        exercise.delete()
        messages.success(request, "Exercise deleted successfully!")
    return redirect('exercise_list')            