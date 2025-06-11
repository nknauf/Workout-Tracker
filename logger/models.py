from django.db import models
from django.contrib.auth.models import User

class MuscleGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class SubMuscleGroup(models.Model):
    name = models.CharField(max_length=100)
    parent_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE, related_name='sub_groups')

    def __str__(self):
        return self.name
    
class Equipment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class MovementType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class BaseExercise(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    base = models.ForeignKey(BaseExercise, on_delete=models.CASCADE, related_name='variants', null=True)
    name = models.CharField(max_length=200)
    muscle_group = models.ManyToManyField(MuscleGroup)
    equipment = models.ManyToManyField(Equipment)
    movement_type = models.ManyToManyField(MovementType)

    def __str__(self):
        return self.name

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    food = models.ManyToManyField('CalorieEntry', blank=True, related_name='daily_logs')
    workouts = models.ManyToManyField('Workout', blank=True, related_name='daily_logs')

class CalorieEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, null=True, blank=True)
    exercises = models.ManyToManyField(Exercise)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name