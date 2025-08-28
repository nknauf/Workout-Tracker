from django.contrib import admin
from .models import (
    MuscleGroup, Equipment, Exercise, Workout, WorkoutExercise, 
    MealEntry, DailyLog, SavedWorkout, SavedWorkoutExercise
)


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_primary_exercise_count', 'get_secondary_exercise_count']
    search_fields = ['name']
    ordering = ['name']
    
    def get_primary_exercise_count(self, obj):
        return obj.primary_exercises.count()
    get_primary_exercise_count.short_description = 'Primary Exercises'
    
    def get_secondary_exercise_count(self, obj):
        return obj.secondary_exercises.count()
    get_secondary_exercise_count.short_description = 'Secondary Exercises'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_exercise_count']
    search_fields = ['name']
    ordering = ['name']
    
    def get_exercise_count(self, obj):
        return obj.exercise_set.count()
    get_exercise_count.short_description = 'Exercises Using This'


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'primary_muscle_group', 'equipment', 'get_secondary_muscles', 'created_at']
    list_filter = ['primary_muscle_group', 'equipment', 'secondary_muscle_groups', 'created_at']
    filter_horizontal = ['secondary_muscle_groups']
    search_fields = ['name', 'notes', 'primary_muscle_group__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['name']

    def get_secondary_muscles(self, obj):
        secondary = obj.secondary_muscle_groups.all()[:3]
        result = ", ".join([mg.name for mg in secondary])
        if obj.secondary_muscle_groups.count() > 3:
            result += f" (+{obj.secondary_muscle_groups.count() - 3} more)"
        return result or "None"
    get_secondary_muscles.short_description = 'Secondary Muscles'

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'primary_muscle_group', 'equipment')
        }),
        ('Secondary Muscles', {
            'fields': ('secondary_muscle_groups',)
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        })
    )


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1
    fields = ['exercise', 'sets', 'reps', 'weight', 'rest_seconds', 'order', 'notes']
    ordering = ['order']


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'date', 'get_exercise_count', 'created_at']
    list_filter = ['date', 'user', 'created_at']
    search_fields = ['name', 'user__username', 'user__first_name', 'user__last_name', 'notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    inlines = [WorkoutExerciseInline]
    ordering = ['-date', '-created_at']
    
    def get_exercise_count(self, obj):
        return obj.workoutexercise_set.count()
    get_exercise_count.short_description = 'Exercises'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'date')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ['workout', 'exercise', 'sets', 'reps', 'weight', 'order']
    list_filter = ['workout__date', 'exercise__primary_muscle_group', 'sets', 'workout__user']
    search_fields = ['workout__name', 'exercise__name', 'notes']
    ordering = ['workout__date', 'workout', 'order']
    readonly_fields = ['get_primary_muscle']
    
    def get_primary_muscle(self, obj):
        return obj.exercise.primary_muscle_group.name
    get_primary_muscle.short_description = 'Primary Muscle'

    fieldsets = (
        ('Workout Details', {
            'fields': ('workout', 'exercise', 'order')
        }),
        ('Exercise Parameters', {
            'fields': ('sets', 'reps', 'weight', 'rest_seconds')
        }),
        ('Additional Info', {
            'fields': ('notes', 'get_primary_muscle'),
            'classes': ('collapse',)
        })
    )


@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'date', 'calories', 'protein', 'carbs', 'fats']
    list_filter = ['date', 'user', 'created_at']
    search_fields = ['name', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    ordering = ['-date', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'date')
        }),
        ('Nutritional Information', {
            'fields': ('calories', 'protein', 'carbs', 'fats')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'get_workout_count', 'get_meal_count', 'total_calories', 'total_protein']
    list_filter = ['date', 'user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    filter_horizontal = ['workouts', 'meals']
    date_hierarchy = 'date'
    ordering = ['-date']

    def get_workout_count(self, obj):
        return obj.workouts.count()
    get_workout_count.short_description = 'Workouts'

    def get_meal_count(self, obj):
        return obj.meals.count()
    get_meal_count.short_description = 'Meals'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'date')
        }),
        ('Daily Activities', {
            'fields': ('workouts', 'meals')
        }),
        ('Nutritional Totals', {
            'fields': ('total_calories', 'total_protein', 'total_carbs', 'total_fats'),
            'description': 'These totals should match the sum of all meals for this date.'
        })
    )


class SavedWorkoutExerciseInline(admin.TabularInline):
    model = SavedWorkoutExercise
    extra = 1
    fields = ['exercise', 'default_sets', 'default_reps', 'default_weight', 'default_rest_seconds', 'order', 'notes']
    ordering = ['order']


@admin.register(SavedWorkout)
class SavedWorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_favorite', 'times_used', 'last_used', 'get_exercise_count', 'created_at']
    list_filter = ['is_favorite', 'user', 'created_at', 'last_used']
    search_fields = ['name', 'description', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['times_used', 'last_used', 'created_at']
    date_hierarchy = 'created_at'
    inlines = [SavedWorkoutExerciseInline]
    ordering = ['-is_favorite', '-last_used', '-times_used', 'name']
    
    def get_exercise_count(self, obj):
        return obj.saved_exercises.count()
    get_exercise_count.short_description = 'Exercises'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'is_favorite')
        }),
        ('Usage Statistics', {
            'fields': ('times_used', 'last_used', 'created_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['mark_as_favorite', 'mark_as_not_favorite', 'reset_usage_stats']

    def mark_as_favorite(self, request, queryset):
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f'{updated} saved workout(s) marked as favorite.')
    mark_as_favorite.short_description = "Mark selected workouts as favorite"

    def mark_as_not_favorite(self, request, queryset):
        updated = queryset.update(is_favorite=False)
        self.message_user(request, f'{updated} saved workout(s) unmarked as favorite.')
    mark_as_not_favorite.short_description = "Unmark selected workouts as favorite"

    def reset_usage_stats(self, request, queryset):
        updated = queryset.update(times_used=0, last_used=None)
        self.message_user(request, f'Usage statistics reset for {updated} saved workout(s).')
    reset_usage_stats.short_description = "Reset usage statistics"


@admin.register(SavedWorkoutExercise)
class SavedWorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ['saved_workout', 'exercise', 'default_sets', 'default_reps', 'default_weight', 'order']
    list_filter = ['saved_workout__user', 'exercise__primary_muscle_group', 'default_sets']
    search_fields = ['saved_workout__name', 'exercise__name', 'notes']
    ordering = ['saved_workout__name', 'order']
    readonly_fields = ['get_primary_muscle', 'get_equipment']
    
    def get_primary_muscle(self, obj):
        return obj.exercise.primary_muscle_group.name
    get_primary_muscle.short_description = 'Primary Muscle'
    
    def get_equipment(self, obj):
        return obj.exercise.equipment.name
    get_equipment.short_description = 'Equipment'

    fieldsets = (
        ('Template Details', {
            'fields': ('saved_workout', 'exercise', 'order')
        }),
        ('Default Parameters', {
            'fields': ('default_sets', 'default_reps', 'default_weight', 'default_rest_seconds')
        }),
        ('Exercise Info', {
            'fields': ('get_primary_muscle', 'get_equipment', 'notes'),
            'classes': ('collapse',)
        })
    )