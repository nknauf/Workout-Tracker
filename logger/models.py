from django.db import models
from django.contrib.auth.models import User

class MuscleGroup(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL,related_name='subgroups')

    def __str__(self):
        return self.name
    
class Equipment(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL,related_name='attachments')

    def __str__(self):
        return self.name
    

class MovementType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class BaseExercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Exercise(models.Model):
    base = models.ForeignKey(BaseExercise, on_delete=models.CASCADE, related_name='variants', null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    muscle_group = models.ManyToManyField(MuscleGroup)
    equipment = models.ManyToManyField(Equipment)
    movement_type = models.ManyToManyField(MovementType)

    # variant metrics
    is_single_arm = models.BooleanField(default=False)
    grip_type = models.CharField(max_length=100, blank=True, null=True)
    form_note = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

class CalorieEntry(models.Model):
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, null=True, blank=True)
    food_name = models.CharField(max_length=200)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, null=True, blank=True)
    exercises = models.ManyToManyField(Exercise)

    def __str__(self):
        return self.name