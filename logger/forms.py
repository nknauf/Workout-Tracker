from django import forms
from .models import Exercise, Workout, CalorieEntry

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name','muscle_group','equipment','movement_type']

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['name', 'exercises']
        widgets = {
            'exercises': forms.CheckboxSelectMultiple(),
        }
    
class CalorieForm(forms.ModelForm):
    class Meta:
        model = CalorieEntry
        fields = ['name', 'calories', 'protein']