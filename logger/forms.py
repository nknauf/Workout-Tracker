from django import forms
from .models import Exercise, Workout, MealEntry, Equipment, Muscle, BaseExercise, DropSetExercise, DropSetRound, SuperSetExercise, SuperSetExerciseItem

class BaseExerciseForm(forms.ModelForm):
    class Meta:
        model = BaseExercise
        fields = [
            'name', 'muscle_group',
        ]
        widgets = {
            'muscle_group': forms.CheckboxSelectMultiple(),
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = [
            'base_exercise', 'name', 'muscle_group', 'equipment', 'notes'
        ]
        widgets = {
            'muscle_group': forms.CheckboxSelectMultiple(),
            'equipment': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class DropSetExerciseForm(forms.ModelForm):
    class Meta:
        model = DropSetExercise
        fields = ['name', 'base_exercise', 'description', 'instructions', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'instructions': forms.Textarea(attrs={'rows': 5}),
        }

class DropSetRoundForm(forms.ModelForm):
    class Meta:
        model = DropSetRound
        fields = ['round_number', 'weight', 'reps', 'rest_time_seconds', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class SuperSetExerciseForm(forms.ModelForm):
    class Meta:
        model = SuperSetExercise
        fields = ['name', 'description', 'instructions', 'is_active', 'rest_time_between_sets']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'instructions': forms.Textarea(attrs={'rows': 5}),
        }

class SuperSetExerciseItemForm(forms.ModelForm):
    class Meta:
        model = SuperSetExerciseItem
        fields = ['base_exercise', 'order', 'sets', 'reps', 'weight', 'rest_time_seconds', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MealEntryForm(forms.ModelForm):
    class Meta:
        model = MealEntry
        fields = ['name', 'calories', 'protein', 'carbs', 'fats', 'is_template']
        widgets = {
            'is_template': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ConversationalInputForm(forms.Form):
    """Form for conversational input of workouts and meals"""
    input_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe your workout or meal in natural language...\n\nExamples:\n• "I did 3 sets of 10 reps bench press and 5 sets of 5 deadlifts at 225 lbs"\n• "I ate chicken breast with 250 calories and 35g protein, plus a protein shake"\n• "30 minutes of running followed by 20 pushups"',
            'rows': 6,
            'class': 'conversational-input',
            'style': 'width: 100%; padding: 15px; border-radius: 8px; border: 2px solid #444; background-color: #222; color: #f0f0f0; font-size: 16px; resize: vertical;'
        }),
        label='',
        max_length=1000
    )
    
    input_type = forms.ChoiceField(
        choices=[
            ('auto', 'Auto-detect'),
            ('workout', 'Workout'),
            ('meal', 'Meal')
        ],
        initial='auto',
        widget=forms.Select(attrs={
            'class': 'input-type-select',
            'style': 'padding: 8px; border-radius: 4px; background-color: #333; color: #f0f0f0; border: 1px solid #555;'
        })
    )

class ConfirmationForm(forms.Form):
    """Form for confirming parsed data before saving"""
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'confirmation-checkbox',
            'style': 'transform: scale(1.5); margin-right: 10px;'
        })
    )
    
    # Hidden fields to store the parsed data
    parsed_data = forms.CharField(widget=forms.HiddenInput())
    input_type = forms.CharField(widget=forms.HiddenInput())