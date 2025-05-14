from django.contrib import admin
from logger.models import MuscleGroup, Equipment, Exercise, Workout

admin.site.register(MuscleGroup)
admin.site.register(Exercise)
admin.site.register(Equipment)
admin.site.register(Workout)
