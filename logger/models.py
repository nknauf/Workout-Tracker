from django.db import models
from django.contrib.auth.models import User 


class MuscleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    
class BaseExercise(models.Model):
    name = models.CharField(max_length=100, unique=True)
    primary_muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE, related_name='primary_exercises')
    secondary_muscle_groups = models.ManyToManyField(MuscleGroup, blank=True, related_name='secondary_exercises')

    def __str__(self):
        return self.name

class Exercise(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_exercise = models.ForeignKey(BaseExercise, on_delete=models.CASCADE, related_name="exercises")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='equipment')

    @property
    def primary_muscle_group(self):
        return self.base_exercise.primary_muscle_group 
    
    @property
    def secondary_muscle_groups(self):
        return self.base_exercise.secondary_muscle_groups.all() # Returns QuerySet

    def __str__(self):
        return self.name
    
class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date = models.DateField()
    exercises = models.ManyToManyField(Exercise, through='WorkoutExercise')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date}"
    class Meta:
        ordering = ['-date', '-created_at']

class WorkoutExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=3)
    reps = models.PositiveIntegerField(default=8)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

class SavedWorkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date = models.DateField()
    exercises = models.ManyToManyField(WorkoutExercise)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} - {self.date}"
    class Meta:
        ordering = ['-date', '-created_at']

class MealEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField(blank=True)
    fats = models.PositiveIntegerField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.calories} cal ({self.date})"
    class Meta:
        ordering = ['-date', '-created_at']

class DailyLogPicture(models.Model):
    image = models.ImageField(
        upload_to='daily_logs/pictures/',
        help_text='Upload a pump pic from todays workout.'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name if self.image else "(no image)"

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    workouts = models.ManyToManyField(Workout, blank=True, related_name='daily_logs')
    meals = models.ManyToManyField(MealEntry, blank=True, related_name='daily_logs')
    total_calories = models.PositiveIntegerField(default=0)
    total_protein = models.PositiveIntegerField(default=0)
    total_carbs = models.PositiveIntegerField(default=0)
    total_fats = models.PositiveIntegerField(default=0)
    pictures = models.ManyToManyField(
        'DailyLogPicture',
        blank=True,
        related_name='daily_logs',
        help_text='Pictures uploaded with this daily log.'
    )

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

