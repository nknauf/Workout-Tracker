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
    
class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    exercises = models.ManyToManyField(Exercise)

    def __str__(self):
        return self.name

