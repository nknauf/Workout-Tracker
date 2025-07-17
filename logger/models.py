from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# --- Core Entities ---

class BaseMuscle(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Muscle(models.Model):
    name = models.CharField(max_length=100)
    base_muscle = models.ForeignKey(BaseMuscle, on_delete=models.CASCADE, related_name='muscles')

    def __str__(self):
        return f"{self.base_muscle.name} - {self.name}"

class Equipment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# --- Exercise Models ---

class BaseExercise(models.Model):
    name = models.CharField(max_length=200, unique=True)
    muscle_group = models.ManyToManyField(Muscle)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Exercise(models.Model):
    base_exercise = models.ForeignKey(BaseExercise, on_delete=models.CASCADE, related_name='exercises', null=True, blank=True)
    name = models.CharField(max_length=200)
    muscle_group = models.ManyToManyField(Muscle)
    equipment = models.ManyToManyField(Equipment)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name and self.base_exercise:
            self.name = self.base_exercise.name
        super().save(*args, **kwargs)

# --- Drop Set Models ---

class DropSetExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    base_exercise = models.ForeignKey(BaseExercise, on_delete=models.CASCADE, related_name='drop_sets')
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class DropSetRound(models.Model):
    drop_set = models.ForeignKey(DropSetExercise, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    reps = models.PositiveIntegerField()
    rest_time_seconds = models.PositiveIntegerField(default=0, help_text="Rest time before next round")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['round_number']
        unique_together = ['drop_set', 'round_number']

    def __str__(self):
        return f"{self.drop_set.name} - Round {self.round_number}"

# --- Super Set Models ---

class SuperSetExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    rest_time_between_sets = models.PositiveIntegerField(default=60, help_text="Rest time in seconds between super sets")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class SuperSetExerciseItem(models.Model):
    super_set = models.ForeignKey(SuperSetExercise, on_delete=models.CASCADE, related_name='exercises')
    base_exercise = models.ForeignKey(BaseExercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    sets = models.PositiveIntegerField(default=3)
    reps = models.PositiveIntegerField(default=10)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    rest_time_seconds = models.PositiveIntegerField(default=0, help_text="Rest time after this exercise")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ['super_set', 'order']

    def __str__(self):
        return f"{self.super_set.name} - {self.base_exercise.name} (Order {self.order})"

# --- Meal Entry ---

class MealEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField(default=0)
    fats = models.PositiveIntegerField(default=0)
    is_template = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.calories} cal"

# --- Workout (Polymorphic) ---

class WorkoutExerciseItem(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    workout = models.ForeignKey('Workout', on_delete=models.CASCADE, related_name='items')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['workout', 'order']

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    items = GenericRelation(WorkoutExerciseItem, related_query_name='workout')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# --- Daily Log ---

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    workouts = models.ManyToManyField(Workout, blank=True, related_name='daily_logs')
    meals = models.ManyToManyField(MealEntry, blank=True, related_name='daily_logs')

    def __str__(self):
        return f"{self.user.username} - {self.date}"

# --- Templates ---

class WorkoutTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    items = GenericRelation(WorkoutExerciseItem, related_query_name='workout_template')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MealTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField(default=0)
    fats = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name