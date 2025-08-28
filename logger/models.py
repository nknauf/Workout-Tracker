from django.db import models
from django.contrib.auth.models import User

# --- Core Entities ---

class MuscleGroup(models.Model):
    """Generic muscle groups'"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Equipment(models.Model):
    """Equipment types, exluding speific machines and attachments"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Exercise(models.Model):
    """Single exercise model - no complexity"""
    name = models.CharField(max_length=200, unique=True)
    primary_muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE, related_name='primary_exercises')
    secondary_muscle_groups = models.ManyToManyField(MuscleGroup, blank=True, related_name='secondary_exercises')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Workout(models.Model):
    """Simple workout - no templates"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date = models.DateField()
    exercises = models.ManyToManyField(Exercise, through='WorkoutExercise')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    class Meta:
        ordering = ['-date', '-created_at']

class WorkoutExercise(models.Model):
    """Junction table for workout-exercise relationship with exercise-specific data"""
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=3)
    reps = models.PositiveIntegerField(default=10)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    rest_seconds = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)  # Order within the workout
    
    class Meta:
        ordering = ['order']
        unique_together = ['workout', 'exercise']

class MealEntry(models.Model):
    """Simple meal entry"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField(default=0)
    fats = models.PositiveIntegerField(default=0)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.calories} cal ({self.date})"
    
    class Meta:
        ordering = ['-date', '-created_at']

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    workouts = models.ManyToManyField(Workout, blank=True, related_name='daily_logs')
    meals = models.ManyToManyField(MealEntry, blank=True, related_name='daily_logs')
    total_calories = models.PositiveIntegerField(default=0)
    total_protein = models.PositiveIntegerField(default=0)
    total_carbs = models.PositiveIntegerField(default=0)
    total_fats = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class SavedWorkout(models.Model):
    """Saved workout templates that users can reuse"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)  # "Push Day A", "Leg Day", "Quick Arms"
    description = models.TextField(blank=True)  # Optional notes about the workout
    exercises = models.ManyToManyField(Exercise, through='SavedWorkoutExercise')
    is_favorite = models.BooleanField(default=False)  # Pin favorites to top
    times_used = models.PositiveIntegerField(default=0)  # Track popularity
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-is_favorite', '-last_used', '-times_used', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def create_workout_from_template(self, date=None, name_override=None):
        """Create a new Workout based on this saved workout"""
        from datetime import date as dt_date
        
        # Create the new workout
        workout = Workout.objects.create(
            user=self.user,
            name=name_override or f"{self.name} - {date or dt_date.today()}",
            date=date or dt_date.today(),
            notes=f"Created from saved workout: {self.name}"
        )
        
        # Copy all exercises with their default values
        for saved_exercise in self.saved_exercises.all():
            WorkoutExercise.objects.create(
                workout=workout,
                exercise=saved_exercise.exercise,
                sets=saved_exercise.default_sets,
                reps=saved_exercise.default_reps,
                weight=saved_exercise.default_weight,
                rest_seconds=saved_exercise.default_rest_seconds,
                notes=saved_exercise.notes,
                order=saved_exercise.order
            )
        
        # Update usage stats
        self.times_used += 1
        self.last_used = workout.created_at
        self.save()
        
        return workout

class SavedWorkoutExercise(models.Model):
    """Junction table for SavedWorkout-Exercise with default values"""
    saved_workout = models.ForeignKey(SavedWorkout, on_delete=models.CASCADE, related_name='saved_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    default_sets = models.PositiveIntegerField(default=3)
    default_reps = models.PositiveIntegerField(default=10)
    default_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    default_rest_seconds = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)  # Exercise-specific notes for this template
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['saved_workout', 'exercise']
    
    def __str__(self):
        return f"{self.saved_workout.name} - {self.exercise.name}"

# Implement in future for more complex saved workout management
# class SavedWorkoutManager(models.Manager):
#     def popular_for_user(self, user, limit=5):
#         """Get most popular saved workouts for a user"""
#         return self.filter(user=user).order_by('-times_used')[:limit]
    
#     def recent_for_user(self, user, limit=5):
#         """Get recently used saved workouts for a user"""
#         return self.filter(user=user, last_used__isnull=False).order_by('-last_used')[:limit]
