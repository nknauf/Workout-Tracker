from django.contrib import admin
from .models import (
    MuscleGroup, Equipment, Exercise, Workout, WorkoutExercise, 
    MealEntry, DailyLog, BaseExercise, SavedWorkout, Follow, UserProfile, Post, PostImage,
    PostLike, Comment,
)

@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 1


@admin.register(BaseExercise)
class BaseExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "primary_muscle_group_display")
    search_fields = ("name", "primary_muscle_group__name")
    list_filter = ("primary_muscle_group",)
    inlines = [ExerciseInline]

    def primary_muscle_group_display(self, obj):
        return obj.primary_muscle_group.name
    primary_muscle_group_display.short_description = "Primary Muscle"


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "base_exercise", "equipment")
    search_fields = ("name", "base_exercise__name", "equipment__name")
    list_filter = ("equipment",)


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "date", "created_at")
    search_fields = ("name", "user__username")
    list_filter = ("date", "user")
    inlines = [WorkoutExerciseInline]


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "workout", "exercise", "sets", "reps", "weight", "order")
    search_fields = ("name", "exercise__name", "user__username")
    list_filter = ("user", "workout")


@admin.register(SavedWorkout)
class SavedWorkoutAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "date", "created_at")
    search_fields = ("name", "user__username")
    list_filter = ("date", "user")


@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "calories", "protein", "carbs", "fats", "date")
    search_fields = ("name", "user__username")
    list_filter = ("date", "user")
    ordering = ("-date",)


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = (
        "user", "date",
        "total_calories", "total_protein", "total_carbs", "total_fats"
    )
    search_fields = ("user__username",)
    list_filter = ("date", "user")
    ordering = ("-date",)


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "visibility", "created_at")
    list_filter = ("visibility", "created_at")
    search_fields = ("author__username", "content")
    inlines = [PostImageInline]


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "created_at")


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "created_at")
    search_fields = ("content", "user__username")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("author", "visibility", "created_at")
    search_fields = ("author__username",)

