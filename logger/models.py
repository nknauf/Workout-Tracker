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
    workout = models.ForeignKey('Workout', on_delete=models.CASCADE, null=True, related_name='exercise_items')
    template = models.ForeignKey('WorkoutTemplate', on_delete=models.CASCADE, null=True, related_name='exercise_items')
    order = models.PositiveIntegerField(default=0)
    working_sets = models.PositiveIntegerField(default=0)
    max_weight = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_weight_reps = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ['workout', 'order']


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_exercises(self):
        """Get all exercises in this workout in order"""
        return [item.content_object for item in self.exercise_items.all()]
    
    def add_exercise(self, exercise):
        """Add an exercise to the workout"""
        next_order = self.exercise_items.count()
        WorkoutExerciseItem.objects.create(
            workout=self,
            content_type=ContentType.objects.get_for_model(exercise),
            object_id=exercise.id,
            order=next_order
        )
    
    def remove_exercise(self, exercise):
        """Remove an exercise from the workout"""
        exercise_type = ContentType.objects.get_for_model(exercise)
        item = self.exercise_items.filter(
            content_type=exercise_type,
            object_id=exercise.id
        ).first()
        if item:
            item.delete()
            self.reorder_items()

    def reorder_items(self):
        """Reorder all items to ensure sequential order"""
        items = self.exercise_items.all()
        for index, item in enumerate(items):
            item.order = index
            item.save()

    def __str__(self):
        return self.name

# --- Daily Log ---

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    workouts = models.ManyToManyField(Workout, blank=True, related_name='daily_logs')
    workout_templates = models.ManyToManyField('WorkoutTemplate', blank=True, related_name='daily_logs')
    meals = models.ManyToManyField(MealEntry, blank=True, related_name='daily_logs')

    def __str__(self):
        return f"{self.user.username} - {self.date}"

# --- Templates ---

class WorkoutTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_exercises(self):
        """Get all exercises in this workout in order"""
        return [item.content_object for item in self.exercise_items.all()]
    
    def add_exercise(self, exercise):
        """Add an exercise to the workout"""
        next_order = self.exercise_items.count()
        WorkoutExerciseItem.objects.create(
            workout=self,
            content_type=ContentType.objects.get_for_model(exercise),
            object_id=exercise.id,
            order=next_order
        )
    
    def remove_exercise(self, exercise):
        """Remove an exercise from the workout"""
        exercise_type = ContentType.objects.get_for_model(exercise)
        item = self.exercise_items.filter(
            content_type=exercise_type,
            object_id=exercise.id
        ).first()
        if item:
            item.delete()
            self.reorder_items()

    def reorder_items(self):
        """Reorder all items to ensure sequential order"""
        items = self.exercise_items.all()
        for index, item in enumerate(items):
            item.order = index
            item.save()

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