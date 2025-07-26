from django.shortcuts import render, redirect, get_object_or_404
from .forms import ExerciseForm, WorkoutForm, MealEntryForm, ConversationalInputForm, ConfirmationForm, BaseExerciseForm
from .models import (
    Workout, Exercise, Equipment, Muscle, MealEntry, DailyLog, 
    WorkoutTemplate, MealTemplate, BaseMuscle, BaseExercise,
    WorkoutExerciseItem
)
from .nlp_engine import NLPEngine
from .tools import create_workout_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from datetime import date
from django.db.models import Prefetch
from django.utils.dateparse import parse_date
from django.contrib.contenttypes.models import ContentType
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

    # get current session data
    exercises_in_session = request.session.get('workout_exercises', [])

    # Handle workout name
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

        elif 'load_template' in request.POST:
            template_id = request.POST.get('load_template')
            try:
                template = WorkoutTemplate.objects.get(id=template_id, user=request.user)
                exercises_in_session = []

                template_exercise_items = template.exercise_items.all()
                for item in template_exercise_items:
                    # Add safety check for the exercise relationship
                    if hasattr(item, 'exercise') and item.exercise:
                        exercises_in_session.append(str(item.object_id))
                
                request.session['workout_exercises'] = exercises_in_session
                request.session['workout_name'] = template.name
                request.session.modified = True
                messages.success(request, f"Loaded template: {template.name}")
                return redirect(f"{request.path}?workout_name={template.name}")
    
            except WorkoutTemplate.DoesNotExist:
                messages.error(request, "Template not found.")
        
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

        elif 'cancel_workout' in request.POST:
            request.session['workout_exercises'] = []
            if 'workout_name' in request.session:
                del request.session['workout_name']
            request.session.modified = True
            messages.info(request, "Workout creation cancelled.")
            return redirect('home')

        elif 'just_save_workout' in request.POST:
            if exercises_in_session:
                try:
                    # Get or create daily log
                    log, _ = DailyLog.objects.get_or_create(user=request.user, date=date.today())
                    
                    # Create workout name
                    name = workout_name if workout_name else f"Workout for {date.today().strftime('%Y-%m-%d')}"
                    
                    # Create workout
                    workout = Workout.objects.create(user=request.user, name=name)
                    
                    # Add exercises using the workout method
                    for ex_id in exercises_in_session:
                        try:
                            exercise = Exercise.objects.get(id=int(ex_id))
                            workout.add_exercise(exercise)
                        except Exercise.DoesNotExist:
                            messages.warning(request, f"Exercise with ID {ex_id} not found, skipping.")
                            continue
                    
                    # Add workout to daily log
                    log.workouts.add(workout)
                    request.session['workout_exercises'] = []
                    if 'workout_name' in request.session:
                        del request.session['workout_name']
                    messages.success(request, f"Workout '{workout.name}' saved successfully!")
                    return redirect('home')
                    
                except Exception as e:
                    messages.error(request, f"Error saving workout: {str(e)}")
                    # Clear session even on error
                    request.session['workout_exercises'] = []
                    if 'workout_name' in request.session:
                        del request.session['workout_name']
                    request.session.modified = True
                    return redirect('create_workout')
                
            else:
                messages.warning(request, "No exercises selected to save.")
                return redirect('create_workout')
        
        elif 'save_workout_and_template' in request.POST:
            if exercises_in_session:
                try:
                    # Get or create daily log
                    log, _ = DailyLog.objects.get_or_create(user=request.user, date=date.today())

                    # Create workout name
                    name = workout_name if workout_name else f"Workout for {date.today().strftime('%Y-%m-%d')}"
                    
                    # Create workout
                    workout = Workout.objects.create(user=request.user, name=name)
                    
                    # Add exercises using the workout method
                    for ex_id in exercises_in_session:
                        try:
                            exercise = Exercise.objects.get(id=int(ex_id))
                            workout.add_exercise(exercise)
                        except Exercise.DoesNotExist:
                            messages.warning(request, f"Exercise with ID {ex_id} not found, skipping.")
                            continue
                    
                    log.workouts.add(workout)

                    # Save as template
                    template = create_workout_template(request.user, workout)
                    
                    # Add template to daily log (if this relationship exists)
                    if hasattr(log, 'workout_templates'):
                        log.workout_templates.add(template)

                    request.session['workout_exercises'] = []
                    if 'workout_name' in request.session:
                        del request.session['workout_name']
                    if 'workout_name' in request.session:
                        del request.session['workout_name']
                    request.session.modified = True
                    
                    messages.success(request, f"Workout '{workout.name}' saved and template created successfully!")
                    return redirect('home')
                    
                except Exception as e:
                    messages.error(request, f"Error saving workout: {str(e)}")
                    request.session['workout_exercises'] = []
                    if 'workout_name' in request.session:
                        del request.session['workout_name']
                    request.session.modified = True
                    return redirect('create_workout')
            
            else:
                messages.warning(request, "No exercises selected to save.")
                return redirect('create_workout')
            
    # Fetching filters from the request
    selected_muscles = request.GET.getlist('muscle_group')
    equipment_filter = request.GET.getlist('equipment')

    exercises = Exercise.objects.all()
    
    available_exercises = exercises
    if equipment_filter:
        available_exercises = available_exercises.filter(equipment__id__in=equipment_filter)
    if selected_muscles:
        available_exercises = available_exercises.filter(muscle_group__id__in=selected_muscles)

    # Remove already selected exercsies from available list
    available_exercises = available_exercises.exclude(id__in=exercises_in_session)
    selected_exercises = Exercise.objects.filter(id__in=exercises_in_session)

    if not workout_name:
        workout_name = request.session.get('workout_name', '')

    saved_templates = WorkoutTemplate.objects.filter(user=request.user).order_by('-created_at')[:20]
    saved_templates_data = []

    for template in saved_templates:
        try:
            template_exercise_items = template.exercise_items.all()
            exercise_names = []
            
            for item in template_exercise_items:
                if hasattr(item, 'exercise') and item.exercise:
                    exercise_names.append(item.exercise.name)

            saved_templates_data.append({
                'id': template.id,
                'name': template.name,
                'created_at': template.created_at,
                'exercise_count': len(exercise_names),
                'exercise_names': ', '.join(exercise_names),
                'type': 'template'
            })
        except Exception as e:
            # Log the error but continue processing other templates
            continue

    saved_items = saved_templates_data
    saved_items.sort(key=lambda x: x['created_at'], reverse=True)

    context = {
        'workout_name': workout_name,
        'available_exercises': available_exercises.distinct(),
        'muscles': Muscle.objects.all(),
        'equipment': Equipment.objects.all(),
        'selected_muscles': [int(m) for m in selected_muscles],
        'selected_equipment': [int(e) for e in equipment_filter],
        'selected_exercises': selected_exercises,
        'saved_items' : saved_items,
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

    workouts = daily_log.workouts.all().prefetch_related(
        'exercise_items',
        'exercise_items__content_object'
        )
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

    if request.method == 'GET' and not request.session.get('workout_exercises'):
        # Load existing workout items into session
        exercises_in_session = []
        workout_exercise_items = workout.exercise_items.all()

        for item in workout_exercise_items:
            if item.content_type.model == 'exercise':
                exercises_in_session.append(str(item.object_id))
        
        request.session['workout_exercises'] = exercises_in_session
        request.session.modified = True

    if request.method == 'POST':
        workout_name = request.POST.get('workout_name', workout.name)

        if 'update_name' in request.POST:
            workout.name = workout_name
            workout.save()
            messages.success(request, "Workout name updated successfully!")

        if 'add_exercise' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id:
                if 'workout_exercises' not in request.session:
                    request.session['workout_exercises'] = []
                if exercise_id not in request.session['workout_exercises']:
                    request.session['workout_exercises'].append(exercise_id)
                    request.session.modified = True
                    messages.success(request, "Exercise added to workout!")
            request.session.modified = True

        if 'remove_exercise' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            if exercise_id and 'workout_exercises' in request.session:
                request.session['workout_exercises'].remove(exercise_id)
                request.session.modified = True
                messages.success(request, "Exercise removed from workout!")

        elif 'cancel_workout' in request.POST:
            request.session['workout_exercises'] = []
            if 'workout_name' in request.session:
                del request.session['workout_name']
            request.session.modified = True
            messages.info(request, "Workout creation cancelled.")
            return redirect('home')
            
        elif 'save_workout' in request.POST:
            workout.name = workout_name
            workout.save()
            
            # Clear existing items and recreate
            workout.exercise_items.all().delete()
            
            order = 0
            # Add exercises
            for ex_id in request.session.get('workout_exercises', []):
                try:
                    exercise = Exercise.objects.get(id=int(ex_id))
                    WorkoutExerciseItem.objects.create(
                        workout=workout,
                        content_type=ContentType.objects.get_for_model(Exercise),
                        object_id=exercise.id,
                        order=order
                    )
                    order += 1
                except Exercise.DoesNotExist:
                    # Skip if exercise doesn't exist
                    continue
            
            messages.success(request, "Workout updated successfully!")
            if 'workout_exercises' in request.session:
                del request.session['workout_exercises']
            return redirect('calendar')
                
    muscle_ids = request.GET.getlist('muscle_group')
    equipment_filter = request.GET.getlist('equipment')

    exercises = Exercise.objects.all()
    
    if equipment_filter:
        exercises = exercises.filter(equipment__id__in=equipment_filter)
    if muscle_ids:
        exercises = exercises.filter(muscle_group__id__in=muscle_ids)

    context = {
        'workout_name': workout.name,
        'available_exercises': exercises,
        'selected_exercises': Exercise.objects.filter(id__in=request.session.get('workout_exercises', [])),
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


# New Claude written views for NLP processing


@login_required
def conversational_input(request):
    """
    Handle conversational input for workouts and meals
    """
    if request.method == 'POST':
        form = ConversationalInputForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['input_text']
            input_type = form.cleaned_data['input_type']
            
            nlp = NLPEngine()
            
            # Auto-detect if input_type is 'auto'
            if input_type == 'auto':
                if nlp._classify_as_workout(input_text):
                    input_type = 'workout'
                else:
                    input_type = 'meal'  # Default to meal for now
            
            if input_type == 'workout':
                # Process workout input
                result = nlp.process_workout_input(input_text, request.user)
                
                if result['success']:
                    # Convert exercises to serializable format
                    serializable_result = nlp.process_workout_input(input_text, request.user)

                    # Store result in session for confirmation
                    request.session['nlp_workout_result'] = serializable_result 
                    request.session['nlp_input_text'] = input_text
                    return redirect('confirm_nlp_workout')
                else:
                    messages.error(request, f"Could not parse workout: {result['message']}")
            
            elif input_type == 'meal':
                # For now, redirect to regular meal logging
                messages.info(request, "Meal parsing not yet implemented. Redirecting to regular meal entry.")
                return redirect('log_meal_entry')
    
    else:
        form = ConversationalInputForm()
    
    return render(request, 'logger/conversational_input.html', {'form': form})

def convert_nlp_result_to_serializable(result):
    """
    Convert NLP result with Django model objects to JSON-serializable format
    """
    serializable_result = result.copy()
    
    # Convert exercises to serializable format
    serializable_exercises = []
    for exercise_data in result.get('exercises', []):
        serializable_exercise = exercise_data.copy()
        
        # Convert db_match (Exercise object) to dict
        if serializable_exercise.get('db_match'):
            db_match = serializable_exercise['db_match']
            serializable_exercise['db_match'] = {
                'id': db_match.id,
                'name': db_match.name,
                'notes': db_match.notes or ''
            }
        
        # Convert suggested_exercises to list of dicts
        if serializable_exercise.get('suggested_exercises'):
            serializable_exercise['suggested_exercises'] = [
                {
                    'id': ex.id,
                    'name': ex.name,
                    'notes': ex.notes or ''
                }
                for ex in serializable_exercise['suggested_exercises']
            ]
        
        serializable_exercises.append(serializable_exercise)
    
    serializable_result['exercises'] = serializable_exercises
    return serializable_result

def convert_serializable_to_nlp_result(serializable_result):
    """
    Convert serializable result back to format with Django objects
    """
    result = serializable_result.copy()
    
    # Convert exercises back to format with model objects
    exercises_with_objects = []
    for exercise_data in serializable_result.get('exercises', []):
        exercise_with_objects = exercise_data.copy()
        
        # Convert db_match dict back to Exercise object
        if exercise_data.get('db_match'):
            try:
                db_match_data = exercise_data['db_match']
                exercise_with_objects['db_match'] = Exercise.objects.get(
                    id=db_match_data['id']
                )
            except Exercise.DoesNotExist:
                exercise_with_objects['db_match'] = None
        
        # Convert suggested_exercises back to Exercise objects
        if exercise_data.get('suggested_exercises'):
            suggested_ids = [ex['id'] for ex in exercise_data['suggested_exercises']]
            exercise_with_objects['suggested_exercises'] = list(
                Exercise.objects.filter(id__in=suggested_ids)
            )
        
        exercises_with_objects.append(exercise_with_objects)
    
    result['exercises'] = exercises_with_objects
    return result

@login_required
def confirm_nlp_workout(request):
    """
    Confirm and edit NLP-parsed workout before saving
    """
    serializable_result = request.session.get('nlp_workout_result')
    input_text = request.session.get('nlp_input_text', '')
    
    if not serializable_result:
        messages.error(request, "No workout data to confirm. Please try again.")
        return redirect('conversational_input')
    
    nlp_result = convert_serializable_to_nlp_result(serializable_result)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_workout':
            # Create the workout
            nlp = NLPEngine()
            create_result = nlp.create_workout_from_nlp(nlp_result, request.user)
            
            if create_result['success']:
                messages.success(request, create_result['message'])
                # Clear session data
                if 'nlp_workout_result' in request.session:
                    del request.session['nlp_workout_result']
                if 'nlp_input_text' in request.session:
                    del request.session['nlp_input_text']
                return redirect('home')
            else:
                messages.error(request, create_result['message'])
        
        elif action == 'create_missing':
            # Create missing exercises
            nlp = NLPEngine()
            create_result = nlp.create_missing_exercises(nlp_result, request.user)
            
            if create_result['count'] > 0:
                messages.success(request, f"Created {create_result['count']} new exercises.")
                # Update the session with new exercise matches
                updated_result = nlp.process_workout_input(input_text, request.user)
                request.session['nlp_workout_result'] = updated_result
            else:
                messages.info(request, "No exercises were created.")
        
        elif action == 'edit_workout':
            # Allow editing of workout name and exercise details
            workout_name = request.POST.get('workout_name', nlp_result['workout_name'])
            nlp_result['workout_name'] = workout_name
            
            # Update exercise details
            for i, exercise in enumerate(nlp_result['exercises']):
                sets = request.POST.get(f'exercise_sets_{i}')
                reps = request.POST.get(f'exercise_reps_{i}')
                weight = request.POST.get(f'exercise_weight_{i}')
                
                if sets:
                    exercise['sets'] = int(sets)
                if reps:
                    exercise['reps'] = int(reps)
                if weight:
                    exercise['weight'] = int(weight)
            
            serializable_updated = convert_nlp_result_to_serializable(nlp_result)
            request.session['nlp_workout_result'] = serializable_updated
            messages.success(request, "Workout updated successfully.")
    
    # Generate summary for display
    nlp = NLPEngine()
    workout_summary = nlp.get_workout_summary(nlp_result)
    
    context = {
        'nlp_result': nlp_result,
        'input_text': input_text,
        'workout_summary': workout_summary,
        'exercises': nlp_result.get('exercises', []),
        'missing_exercises': [ex for ex in nlp_result.get('exercises', []) if not ex.get('db_match')],
    }
    
    return render(request, 'logger/confirm_nlp_workout.html', context)

@login_required
@csrf_exempt
def api_nlp_process(request):
    """
    API endpoint for processing NLP input (for AJAX requests)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            input_text = data.get('text', '')
            input_type = data.get('type', 'auto')
            
            if not input_text:
                return JsonResponse({
                    'success': False,
                    'message': 'No input text provided'
                })
            
            nlp = NLPEngine()
            
            if input_type == 'auto' or input_type == 'workout':
                result = nlp.process_workout_input(input_text, request.user)
                
                if result['success']:
                    serializable_result = convert_nlp_result_to_serializable(result)
                    return JsonResponse(serializable_result)
                else:
                    return JsonResponse(result)
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Meal processing not yet implemented'
                })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Server error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Only POST requests allowed'
    })

# Update your existing home view to show NLP-created workouts
@login_required
def home(request):
    today = date.today()
    log, created = DailyLog.objects.get_or_create(user=request.user, date=today)
    
    # Get today's workouts (including NLP-created ones)
    todays_workouts = log.workouts.all()
    
    # Get meal entries
    meal_entries = log.meals.filter(user=request.user) if log else []
    total_calories = sum(entry.calories for entry in meal_entries)
    total_protein = sum(entry.protein for entry in meal_entries)
    total_carbs = sum(entry.carbs for entry in meal_entries)
    total_fats = sum(entry.fats for entry in meal_entries)

    return render(request, 'logger/home.html', {
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fats': total_fats,
        'todays_workouts': todays_workouts,
        'workout_count': todays_workouts.count(),
    })

# Add this to your existing calendar view to show NLP workouts
@login_required
def calendar(request):
    selected_date = request.GET.get('date', date.today().isoformat())
    parsed_date = parse_date(selected_date) or date.today()

    daily_log, _ = DailyLog.objects.get_or_create(user=request.user, date=parsed_date)

    meals = daily_log.meals.filter(user=request.user) if daily_log else []
    total_calories = sum(meal.calories for meal in meals)
    total_protein = sum(meal.protein for meal in meals)

    # Get workouts with proper prefetching
    workouts = daily_log.workouts.all().prefetch_related(
        'items__content_type',
        'items__content_object'
    )

    # Add exercise details to workouts
    workouts_with_details = []
    for workout in workouts:
        workout_data = {
            'workout': workout,
            'exercises': [],
            'exercise_count': 0
        }
        
        for item in workout.items.all():
            if item.content_object:
                workout_data['exercises'].append({
                    'name': item.content_object.name,
                    'type': item.content_type.model
                })
                workout_data['exercise_count'] += 1
        
        workouts_with_details.append(workout_data)

    return render(request, 'logger/calendar.html', {
        'workouts_with_details': workouts_with_details,
        'selected_date': selected_date,
        'date': parsed_date,
        'meals': meals,
        'total_calories': total_calories,
        'total_protein': total_protein,
    })