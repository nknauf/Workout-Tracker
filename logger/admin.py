from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    Equipment, Exercise, Workout, MealEntry, DailyLog, WorkoutTemplate, 
    MealTemplate, BaseMuscle, Muscle, BaseExercise, WorkoutExerciseItem
)


class MuscleInline(admin.TabularInline):
    model = Muscle
    extra = 1


@admin.register(BaseMuscle)
class BaseMuscleAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_muscle_count']
    search_fields = ['name']
    inlines = [MuscleInline]
    
    def get_muscle_count(self, obj):
        return obj.muscles.count()
    get_muscle_count.short_description = 'Specific Muscles'


@admin.register(Muscle)
class MuscleAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_muscle']
    list_filter = ['base_muscle']
    search_fields = ['name', 'base_muscle__name']
    ordering = ['base_muscle__name', 'name']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 1
    fields = ['name', 'notes']
    show_change_link = True


@admin.register(BaseExercise)
class BaseExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_muscle_groups', 'get_exercise_count', 'created_at']
    list_filter = ['muscle_group', 'created_at']
    filter_horizontal = ['muscle_group']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ExerciseInline]
    date_hierarchy = 'created_at'

    def get_muscle_groups(self, obj):
        return ", ".join([mg.name for mg in obj.muscle_group.all()[:3]])
    get_muscle_groups.short_description = 'Primary Muscles'
    
    def get_exercise_count(self, obj):
        return obj.exercises.count()
    get_exercise_count.short_description = 'Variations'


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_exercise', 'get_muscle_groups', 'get_equipment', 'created_at']
    list_filter = ['base_exercise', 'muscle_group', 'equipment', 'created_at']
    filter_horizontal = ['muscle_group', 'equipment']
    search_fields = ['name', 'base_exercise__name', 'notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['name']

    def get_muscle_groups(self, obj):
        muscles = obj.muscle_group.all()[:3]
        result = ", ".join([mg.name for mg in muscles])
        if obj.muscle_group.count() > 3:
            result += f" (+{obj.muscle_group.count() - 3} more)"
        return result
    get_muscle_groups.short_description = 'Muscles'

    def get_equipment(self, obj):
        equipment = obj.equipment.all()[:3]
        result = ", ".join([eq.name for eq in equipment])
        if obj.equipment.count() > 3:
            result += f" (+{obj.equipment.count() - 3} more)"
        return result
    get_equipment.short_description = 'Equipment'


class WorkoutExerciseItemInline(admin.TabularInline):
    model = WorkoutExerciseItem
    extra = 1
    fields = ['content_type', 'object_id', 'order', 'working_sets', 'max_weight', 'max_weight_reps', 'notes']
    ordering = ['order']


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'get_exercise_count', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    inlines = [WorkoutExerciseItemInline]
    
    def get_exercise_count(self, obj):
        return obj.exercise_items.count()
    get_exercise_count.short_description = 'Exercises'


@admin.register(WorkoutExerciseItem)
class WorkoutExerciseItemAdmin(admin.ModelAdmin):
    list_display = ['get_parent', 'content_object', 'order', 'working_sets', 'max_weight', 'max_weight_reps']
    list_filter = ['content_type', 'working_sets']
    search_fields = ['workout__name', 'template__name']
    ordering = ['workout', 'template', 'order']
    readonly_fields = ['content_type', 'object_id', 'content_object']
    
    def get_parent(self, obj):
        if obj.workout:
            return f"Workout: {obj.workout.name}"
        elif obj.template:
            return f"Template: {obj.template.name}"
        return "No Parent"
    get_parent.short_description = 'Parent'


@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'calories', 'protein', 'carbs', 'fats', 'is_template', 'created_at']
    list_filter = ['is_template', 'created_at', 'user']
    search_fields = ['name', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'is_template')
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
    list_display = ['user', 'date', 'get_meals_count', 'get_workouts_count', 'get_workout_templates_count']
    list_filter = ['date', 'user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    filter_horizontal = ['meals', 'workouts', 'workout_templates']
    date_hierarchy = 'date'
    ordering = ['-date']

    def get_meals_count(self, obj):
        return obj.meals.count()
    get_meals_count.short_description = 'Meals'

    def get_workouts_count(self, obj):
        return obj.workouts.count()
    get_workouts_count.short_description = 'Workouts'
    
    def get_workout_templates_count(self, obj):
        return obj.workout_templates.count()
    get_workout_templates_count.short_description = 'Templates'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'date')
        }),
        ('Workouts', {
            'fields': ('workouts', 'workout_templates')
        }),
        ('Meals', {
            'fields': ('meals',)
        })
    )


class WorkoutTemplateExerciseItemInline(admin.TabularInline):
    model = WorkoutExerciseItem
    fk_name = 'template'
    extra = 1
    fields = ['content_type', 'object_id', 'order', 'working_sets', 'max_weight', 'max_weight_reps', 'notes']
    ordering = ['order']


@admin.register(WorkoutTemplate)
class WorkoutTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'get_exercise_count', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    inlines = [WorkoutTemplateExerciseItemInline]
    
    def get_exercise_count(self, obj):
        return obj.exercise_items.count()
    get_exercise_count.short_description = 'Exercises'


@admin.register(MealTemplate)
class MealTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'calories', 'protein', 'carbs', 'fats', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name')
        }),
        ('Nutritional Information', {
            'fields': ('calories', 'protein', 'carbs', 'fats')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )