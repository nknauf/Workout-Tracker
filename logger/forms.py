from django import forms
from .models import Exercise, Workout, MealEntry, Equipment, MuscleGroup


class ExerciseForm(forms.ModelForm):
    """Form for creating/editing exercises"""
    class Meta:
        model = Exercise
        fields = ['name', 'base_exercise', 'equipment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter exercise name (e.g., Bench Press)'
            }),
            'primary_muscle_group': forms.Select(attrs={'class': 'form-select'}),
            'secondary_muscle_groups': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this exercise...'
            }),
        }
        labels = {
            'primary_muscle_group': 'Primary Muscle Group',
            'secondary_muscle_groups': 'Secondary Muscle Groups (optional)',
            'equipment': 'Equipment Required',
        }


class WorkoutForm(forms.ModelForm):
    """Simple form for workout name"""
    class Meta:
        model = Workout
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter workout name (e.g., Upper Body Push)'
            }),
        }


class MealEntryForm(forms.ModelForm):
    """Form for logging meal entries"""
    class Meta:
        model = MealEntry
        fields = ['name', 'calories', 'protein', 'carbs', 'fats']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meal name (e.g., Chicken & Rice)'
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Calories'
            }),
            'protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Protein (g)'
            }),
            'carbs': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Carbs (g)'
            }),
            'fats': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Fats (g)'
            })
        }


class ExerciseFilterForm(forms.Form):
    """Form for filtering exercises in workout creation"""
    muscle_group = forms.ModelMultipleChoiceField(
        queryset=MuscleGroup.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Filter by Muscle Group'
    )
    
    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Filter by Equipment'
    )


class WorkoutExerciseForm(forms.Form):
    """Form for adding exercise details to workout"""
    sets = forms.IntegerField(
        initial=3,
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'style': 'width: 80px;'
        })
    )
    
    reps = forms.IntegerField(
        initial=10,
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'style': 'width: 80px;'
        })
    )
    
    weight = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'style': 'width: 100px;',
            'placeholder': 'Weight',
            'step': '0.5'
        })
    )


class DateFilterForm(forms.Form):
    """Form for filtering by date range"""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='From Date'
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='To Date'
    )


class QuickMealForm(forms.Form):
    """Quick form for common meal logging"""
    MEAL_CHOICES = [
        ('protein_shake', 'Protein Shake (300 cal, 30g protein)'),
        ('chicken_rice', 'Chicken & Rice (550 cal, 45g protein, 60g carbs)'),
        ('oatmeal', 'Oatmeal with Banana (400 cal, 12g protein, 65g carbs)'),
        ('greek_yogurt', 'Greek Yogurt (200 cal, 15g protein, 25g carbs)'),
        ('custom', 'Custom meal (fill details below)'),
    ]
    
    meal_type = forms.ChoiceField(
        choices=MEAL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'updateMealFields(this.value)'
        }),
        label='Quick Meal Selection'
    )
    
    # These fields will be auto-filled based on selection
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Meal name'
        })
    )
    
    calories = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    protein = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    carbs = forms.IntegerField(
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    fats = forms.IntegerField(
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )