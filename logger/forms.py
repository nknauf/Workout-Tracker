from django import forms
from .models import Exercise, Workout, CalorieEntry

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name','description','muscle_group','equipment']
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
        }

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
        fields = ['food_name', 'calories', 'protein']