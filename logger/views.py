from django.shortcuts import render, redirect
from .forms import ExerciseForm, WorkoutForm, CalorieForm
from .models import Workout, Exercise, Equipment, MuscleGroup, CalorieEntry, DailyLog
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

def home(request):
    return render(request, 'logger/home.html')

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

    # Initialize session list if not already set
    if 'workout_exercises' not in request.session:
        request.session['workout_exercises'] = []

    # Handle exercise selection to add to session
    if request.method == 'POST':

        workout_name = request.POST.get('workout_name', '')

        if 'add_to_workout' in request.POST:
            selected_ids = request.POST.getlist('exercise_ids')
            for id in selected_ids:
                if id not in request.session['workout_exercises']:
                    request.session['workout_exercises'].append(id)
            request.session.modified = True
        elif 'save_workout' in request.POST:
            name = request.POST.get('workout_name', 'Unnamed Workout')
            workout = Workout.objects.create(name=name, user=request.user)
            workout.exercises.set(id__in=request.session['workout_exercises'])
            workout.save()
            request.session['workout_exercises'] = [] # clear session
            messages.success(request, "Workout saved!")
            return redirect('home')
        elif 'remove_exercise' in request.POST:
            to_remove = request.POST.get('remove_exercise')
            if to_remove in request.session['workout_exercises']:
                request.session['workout_exercises'].remove(to_remove)
                request.session.modified = True
    elif request.method == 'GET':
        workout_name = request.GET.get('workout_name')

    # filtering
    selected_ids = request.GET.getlist('muscle_group')
    if selected_ids:
        muscle_groups_filter = MuscleGroup.objects.filter(id__in=selected_ids)
    else:
        muscle_groups_filter = MuscleGroup.objects.none()

    equipment_filter = request.GET.getlist('equipment')
    selected_muscle_ids = selected_ids
    
    # maybe implement
    # muscle_groups_filter = list(map(str, request.GET.getlist('muscle_group'))) 

    muscle_group_map = MuscleGroup.objects.filter(parent__isnull=True)
    sub_group_map = MuscleGroup.objects.exclude(parent__isnull=True)
    group_map = {}
    for parent in muscle_group_map:
        group_map[parent] = sub_group_map.filter(parent=parent)

    expanded_muscle_group = set(mg.id for mg in muscle_groups_filter)
    for m_id in list(expanded_muscle_group):
        children = MuscleGroup.objects.filter(parent_id=m_id)
        expanded_muscle_group.update(c.id for c in children)

    exercises = Exercise.objects.all()
    if equipment_filter:
        exercises = exercises.filter(equipment__id__in=equipment_filter)
    if muscle_groups_filter:
        exercises = exercises.filter(muscle_group__id__in=expanded_muscle_group)
    else:
        exercises = Exercise.objects.none()

    exercises = exercises.distinct()
    
    context = {
        'workout_name': workout_name,
        'muscle_group_map': group_map,
        'available_exercises': exercises,
        'muscle_groups': MuscleGroup.objects.filter(parent__isnull=True),
        'selected_muscles': muscle_groups_filter,
        'selected_muscle_ids': selected_muscle_ids,
        'selected_equipment': equipment_filter,
        'sub_groups': MuscleGroup.objects.exclude(parent__isnull=True),
        'equipment': Equipment.objects.all(),
        'selected_exercises': Exercise.objects.filter(id__in=request.session['workout_exercises']),
    }
    return render(request, 'logger/create_workout.html', context)


@login_required
def log_calories(request):
    log, created = DailyLog.objects.get_or_create(user=request.user, date=date.today())
    if request.method == 'POST':
        form = CalorieForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.daily_log = log
            entry.save()
            return redirect('log_calories')
    else:
        form = CalorieForm()

    entries = CalorieEntry.objects.filter(daily_log=log)
    return render(request, 'logger/log_calories.html', {'form': form, 'entries': entries})