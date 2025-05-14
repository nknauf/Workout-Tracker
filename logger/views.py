from django.shortcuts import render, redirect
from .forms import ExerciseForm, WorkoutForm
from .models import Workout, Exercise, Equipment, MuscleGroup
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
            workout.exercises.set(request.session['workout_exercises'])
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
    mucle_groups_filter = request.GET.getlist('muscle_group')
    sub_groups_filter = request.GET.getlist('subgroup')
    equipment_filter = request.GET.getlist('equipment')

    exercises = Exercise.objects.all()
    if mucle_groups_filter:
        exercises = exercises.filter(muscle_group__id__in=mucle_groups_filter)
    if equipment_filter:
        exercises = exercises.filter(equipment__id__in=equipment_filter)
    
    context = {
        'workout_name': workout_name,
        'available_exercises': exercises,
        'muscle_groups': MuscleGroup.objects.filter(parent__isnull=True),
        'selected_muscles': mucle_groups_filter,
        'selected_equipment': equipment_filter,
        'sub_groups': MuscleGroup.objects.exclude(parent__isnull=True),
        'equipment': Equipment.objects.all(),
        'selected_exercises': Exercise.objects.filter(id__in=request.session['workout_exercises']),
    }
    return render(request, 'logger/create_workout.html', context)
