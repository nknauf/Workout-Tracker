from django.contrib import admin
from logger.models import MuscleGroup, Equipment, Exercise, Workout, CalorieEntry, DailyLog

admin.site.register(MuscleGroup)
admin.site.register(Exercise)
admin.site.register(Equipment)
admin.site.register(Workout)
admin.site.register(DailyLog)
admin.site.register(CalorieEntry)