from django.shortcuts import render, redirect
from .forms import ExerciseForm, WorkoutForm, CalorieForm
from .models import Workout, Exercise, Equipment, MuscleGroup, CalorieEntry, DailyLog, MovementType 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from django.db.models import Prefetch
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404

def home(request):
    today = date.today()
    log = DailyLog.objects.filter(user=request.user, date=today).first()
    if not log:
        log = DailyLog.objects.create(user=request.user, date=today)
    calories_entries = CalorieEntry.objects.filter(user=request.user, daily_log=log) if log else []
    total_calories = sum(entry.calories for entry in calories_entries)
    total_protein = sum(entry.protein for entry in calories_entries)

    return render(request, 'logger/home.html' , {
        'total_calories': total_calories,
        'total_protein': total_protein,
    })

@login_required
def create_exercise(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_exercise')
    else:
        form = ExerciseForm()
    return render(request, 'logger/create_exercise.html', {'form':form})

@login_required
def create_workout(request):

    exercises_in_session = request.session.get('workout_exercises', [])
    if 'workout_exercises' not in request.session:
        request.session['workout_exercises'] = exercises_in_session

    if request.method == 'POST':
        workout_name = request.POST.get('workout_name', '').strip()
    else:
        workout_name = request.GET.get('workout_name', '').strip()


    # Handle exercise selection to add to session
    if request.method == 'POST':

        if 'add_to_workout' in request.POST:
            selected_ids = request.POST.getlist('exercise_ids')
            for id in selected_ids:
                if id not in exercises_in_session:
                    exercises_in_session.append(id)
            request.session['workout_exercises'] = exercises_in_session
            request.session.modified = True
        elif 'remove_exercise' in request.POST:
            to_remove = request.POST.get('remove_exercise')
            if to_remove in exercises_in_session:
                exercises_in_session.remove(to_remove)
                request.session.modified = True
        elif 'save_workout' in request.POST:
            log, _ = DailyLog.objects.get_or_create(user=request.user, date=date.today())
            name = workout_name or "Unname Workout"
            workout = Workout.objects.create(name=name, user=request.user, daily_log=log)
            workout.exercises.set([int(i) for i in exercises_in_session])
            workout.save()
            request.session['workout_exercises'] = [] # clear session
            request.session.modified = True
            messages.success(request, "Workout saved!")
            return redirect('home')

    # Fetching filters from the request
    selected_ids = request.GET.getlist('muscle_group')
    equipment_filter = request.GET.getlist('equipment')
    movement_filter = request.GET.getlist('movement_type')

    exercises = Exercise.objects.all()
    if equipment_filter:
        exercises = exercises.filter(equipment__id__in=equipment_filter)
    if selected_ids:
        exercises = exercises.filter(muscle_group__id__in=selected_ids)
    if movement_filter:
        exercises = exercises.filter(movement_type__id__in=movement_filter)
    
    if not selected_ids and not equipment_filter and not movement_filter:
        exercises = Exercise.objects.none()  # No filters applied, return empty queryset

    
    context = {
        'workout_name': workout_name,
        'available_exercises': exercises.distinct(),
        'muscle_groups': MuscleGroup.objects.all(),
        'selected_muscles': selected_ids,
        'selected_muscle_ids': selected_ids,
        'selected_equipment': equipment_filter,
        'selected_movement': movement_filter,
        'equipment': Equipment.objects.all(),
        'movement_types': MovementType.objects.all(),
        'selected_exercises': Exercise.objects.filter(id__in=exercises_in_session),
    }
    return render(request, 'logger/create_workout.html', context)


@login_required
def log_calories(request):
    log, created = DailyLog.objects.get_or_create(user=request.user, date=date.today())
    if request.method == 'POST':
        form = CalorieForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.daily_log = log
            entry.save()
            return redirect('log_calories')
    else:
        form = CalorieForm()

    entries = CalorieEntry.objects.filter(user=request.user, daily_log=log)
    return render(request, 'logger/log_calories.html', {'form': form, 'entries': entries})


@login_required
def calendar(request):
    selected_date = request.GET.get('date', date.today().isoformat())
    parsed_date = parse_date(selected_date) or date.today()

    daily_log, _ = DailyLog.objects.get_or_create(user=request.user, date=parsed_date)

    meals = CalorieEntry.objects.filter(daily_log=daily_log) if daily_log else []
    total_calories = sum(meal.calories for meal in meals)
    total_protein = sum(meal.protein for meal in meals)

    # previously worked, might implement later
    workouts = Workout.objects.filter(
        user=request.user,
        daily_log__date=parsed_date
    ).prefetch_related('exercises')

    meals = CalorieEntry.objects.filter(
        user=request.user,
        daily_log__date=parsed_date
    ).prefetch_related('daily_log')
    if not workouts:
        messages.info(request, "No workouts found for this date.")


    return render(request, 'logger/calendar.html', {
        'workouts': workouts,
        'selected_date': selected_date,
        'date': parsed_date,
        'workouts': workouts,
        'meals': meals,
        'total_calories': total_calories,
        'total_protein': total_protein,
    })


@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)

    if request.method == 'GET' and (not request.session.get('workout_exercises')):
        request.session['workout_exercises'] = [str(ex.id) for ex in workout.exercises.all()]

    if request.method == 'POST':
        workout_name = request.POST.get('workout_name', workout.name)

        if 'add_to_workout' in request.POST:
            selected_ids = request.POST.getlist('exercise_ids')
            for ex_id in selected_ids:
                if ex_id not in request.session['workout_exercises']:
                    request.session['workout_exercises'].append(ex_id)
            request.session.modified = True
        elif 'save_workout' in request.POST:
            workout.name = workout_name
            workout.exercises.set(request.session['workout_exercises'])
            workout.save()
            messages.success(request, "Workout updated successfully!")
            request.session['workout_exercises'] = []
            return redirect('calendar')
        elif 'remove_exercise' in request.POST:
            to_remove = request.POST.get('remove_exercise')
            if to_remove in request.session['workout_exercises']:
                request.session['workout_exercises'].remove(to_remove)
                request.session.modified = True
    

    muscle_ids = request.GET.getlist('muscle_group')
    equipment_filter = request.GET.getlist('equipment')
    movement_filter = request.GET.getlist('movement_type')

    muscle_group_filter = MuscleGroup.objects.filter(id__in=muscle_ids) if muscle_ids else MuscleGroup.objects.none()
    expanded_muscle_group = set(mg.id for mg in muscle_group_filter)

    exercises = Exercise.objects.all()
    if equipment_filter:
        exercises = exercises.filter(equipment__id__in=equipment_filter)
    if muscle_group_filter:
        exercises = exercises.filter(muscle_group__id__in=expanded_muscle_group)
    if movement_filter:
        exercises = exercises.filter(movement_type__id__in=movement_filter)
        
    if not muscle_ids and not equipment_filter and not movement_filter:
        exercises = Exercise.objects.none()  # No filters applied, return empty queryset

    context = {
        'workout_name': workout.name,
        'available_exercises': exercises,
        'selected_exercises': Exercise.objects.filter(id__in=request.session['workout_exercises']),
        'muscle_groups': MuscleGroup.objects.all(),
        'equipment': Equipment.objects.all(),
        'movement_types': MovementType.objects.all(),
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
    meal = get_object_or_404(CalorieEntry, id=meal_id, user=request.user)
    if request.method == 'POST':
        meal.delete()
        messages.success(request, "Meal log deleted successfully!")
    return redirect('home')

@login_required
def edit_meal_log(request, meal_id):
    meal = get_object_or_404(CalorieEntry, id=meal_id, user=request.user)
    if request.method == 'POST':
        form = CalorieForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()
            messages.success(request, "Meal log updated successfully!")
            return redirect('home')
    else:
        form = CalorieForm(instance=meal)
    return render(request, 'logger/edit_meal_log.html', {'form': form, 'meal': meal})

@login_required
def log_meal_entry(request):
    # View where users can create new meal or log an existing meal entry
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            return redirect
        elif action == 'existing':
            return redirect('select_existing_meal') # need to implement this view
    return render(request, 'logger/log_meal_entry.html', {})

@login_required
def log_workout_entry(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            return redirect('create_workout')
        elif action == 'existing':
            return redirect('select_existing_workout') # need to implement this view
    return render(request, 'logger/log_workout_entry.html', {})

@login_required
def select_existing_workout(request):
    # View where users can select an existing workout to log
    workouts = Workout.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        workout_id = request.POST.get('workout_id')
        action = request.POST.get('log_existing') or request.POST.get('edit_existing')

        if workout_id:
            original_workout = get_object_or_404(Workout, id=workout_id, user=request.user)
            if workout_id:
                original_workout = get_object_or_404(Workout, id=workout_id, user=request.user)
                workout = Workout.objects.create(
                    name=f"{original_workout.name} (Copy)",
                    user=request.user
                )
                workout.exercises.set(original_workout.exercises.all())
            log, _ = DailyLog.objects.get_or_create(user=request.user, date=date.today())
            
            if 'log_existing' in request.POST:
                # Log the existing workout, make no changes
                log.workouts.add(workout)
                messages.success(request, "Workout successfully logged.")
            elif 'edit_existing' in request.POST:
                return redirect('edit_workout', workout_id=workout.id)
    return render (request, 'logger/log_workout_entry.html', {'workouts': workouts})

@login_required
def select_existing_meal(request):
    # View where users can select an existing meal to log or create new
    meals = CalorieEntry.objects.filter(user=request.user).order_by('-id')
    if request.method == 'POST':
        meal_id = request.POST.get('meal_id')
        meal = get_object_or_404(CalorieEntry, id=meal_id, user=request.user)

        if meal_id:
            meal = get_object_or_404(CalorieEntry, id=meal_id, user=request.user)
            log, created = DailyLog.objects.get_or_create(user=request.user, date=date.today())

            if 'log_existing' in request.POST:
                log.food.add(meal)
                messages.success(request, "Meal successfully logged")

            elif 'edit_existing' in request.POST:
                return redirect('edit_meal_log', meal_id=meal.id)
    return render(request, 'logger/log_meal_entry.html', {'meals': meals})
            