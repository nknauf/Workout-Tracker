from django.contrib import admin
from .models import (
    Equipment, Exercise, Workout, MealEntry, DailyLog, WorkoutTemplate, MealTemplate, BaseMuscle, Muscle, BaseExercise, DropSetExercise, DropSetRound, SuperSetExercise, SuperSetExerciseItem, WorkoutExerciseItem
)

@admin.register(BaseMuscle)
class BaseMuscleAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Muscle)
class MuscleAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_muscle']
    list_filter = ['base_muscle']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(DropSetExercise)
class DropSetExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_exercise', 'is_active', 'created_at']
    list_filter = ['is_active', 'base_exercise', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DropSetRound)
class DropSetRoundAdmin(admin.ModelAdmin):
    list_display = ['drop_set', 'round_number', 'weight', 'reps', 'rest_time_seconds']
    list_filter = ['drop_set', 'round_number']
    ordering = ['drop_set', 'round_number']

@admin.register(SuperSetExercise)
class SuperSetExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'rest_time_between_sets', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SuperSetExerciseItem)
class SuperSetExerciseItemAdmin(admin.ModelAdmin):
    list_display = ['super_set', 'base_exercise', 'order', 'sets', 'reps', 'weight']
    list_filter = ['super_set', 'base_exercise', 'order']
    ordering = ['super_set', 'order']

@admin.register(BaseExercise)
class BaseExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_muscle_groups']
    list_filter = ['muscle_group']
    filter_horizontal = ['muscle_group']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    def get_muscle_groups(self, obj):
        return ", ".join([mg.name for mg in obj.muscle_group.all()])
    get_muscle_groups.short_description = 'Muscles'

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_exercise', 'get_muscle_groups', 'get_equipment', 'notes']
    list_filter = ['base_exercise', 'muscle_group', 'equipment']
    filter_horizontal = ['muscle_group', 'equipment']
    search_fields = ['name', 'base_exercise__name']
    readonly_fields = ['created_at']

    def get_muscle_groups(self, obj):
        return ", ".join([mg.name for mg in obj.muscle_group.all()])
    get_muscle_groups.short_description = 'Muscles'

    def get_equipment(self, obj):
        return ", ".join([eq.name for eq in obj.equipment.all()])
    get_equipment.short_description = 'Equipment'

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']

@admin.register(WorkoutExerciseItem)
class WorkoutExerciseItemAdmin(admin.ModelAdmin):
    list_display = ['workout', 'content_object', 'order', 'content_type']
    list_filter = ['workout', 'content_type']
    search_fields = ['workout__name']
    ordering = ['workout', 'order']

@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'calories', 'protein', 'carbs', 'fats', 'is_template', 'created_at']
    list_filter = ['is_template', 'created_at', 'user']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']

@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'get_meals_count', 'get_workouts_count']
    list_filter = ['date', 'user']
    search_fields = ['user__username']
    filter_horizontal = ['meals', 'workouts']

    def get_meals_count(self, obj):
        return obj.meals.count()
    get_meals_count.short_description = 'Meals'

    def get_workouts_count(self, obj):
        return obj.workouts.count()
    get_workouts_count.short_description = 'Workouts'

@admin.register(WorkoutTemplate)
class WorkoutTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']

@admin.register(MealTemplate)
class MealTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'calories', 'protein', 'carbs', 'fats', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']