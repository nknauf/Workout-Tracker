from django.db import models
from django.contrib.auth.models import User 
from django.db.models import Q, UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save


# BEGIN: FITNESS_MODELS
class MuscleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    
class BaseExercise(models.Model):
    name = models.CharField(max_length=100, unique=True)
    primary_muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE, related_name='primary_exercises')
    secondary_muscle_groups = models.ManyToManyField(MuscleGroup, blank=True, related_name='secondary_exercises')

    def __str__(self):
        return self.name

class Exercise(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_exercise = models.ForeignKey(BaseExercise, on_delete=models.CASCADE, related_name="exercises")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='equipment')

    @property
    def primary_muscle_group(self):
        return self.base_exercise.primary_muscle_group 
    
    @property
    def secondary_muscle_groups(self):
        return self.base_exercise.secondary_muscle_groups.all() # Returns QuerySet

    def __str__(self):
        return self.name
    
class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date = models.DateField()
    exercises = models.ManyToManyField(Exercise, through='WorkoutExercise')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date}"
    class Meta:
        ordering = ['-date', '-created_at']

class WorkoutExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=3)
    reps = models.PositiveIntegerField(default=8)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

class SavedWorkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date = models.DateField()
    exercises = models.ManyToManyField(WorkoutExercise)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} - {self.date}"
    class Meta:
        ordering = ['-date', '-created_at']

class MealEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField(blank=True)
    fats = models.PositiveIntegerField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.calories} cal ({self.date})"
    class Meta:
        ordering = ['-date', '-created_at']
# END: FITNESS_MODELS

# BEGIN: DAILYLOG_MODEL
class DailyLogPicture(models.Model):
    image = models.ImageField(
        upload_to='daily_logs/pictures/',
        help_text='Upload a pump pic from todays workout.'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name if self.image else "(no image)"

    
class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    workouts = models.ManyToManyField(Workout, blank=True, related_name='daily_logs')
    meals = models.ManyToManyField(MealEntry, blank=True, related_name='daily_logs')
    total_calories = models.PositiveIntegerField(default=0)
    total_protein = models.PositiveIntegerField(default=0)
    total_carbs = models.PositiveIntegerField(default=0)
    total_fats = models.PositiveIntegerField(default=0)
    pictures = models.ManyToManyField(
        'DailyLogPicture',
        blank=True,
        related_name='daily_logs',
        help_text='Pictures uploaded with this daily log.'
    )

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"
# END: DAILYLOG_MODEL


# BEGIN: SOCIAL_MODELS
class UserProfile(models.Model):
    VISIBILITY_CHOICES = (
    ("friends", "Friends"),
    ("public", "Public"),
    )


    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile_author")
    content = models.TextField(max_length=2000)
    # Optional attachments to your existing domain objects
    workout = models.ForeignKey("Workout", null=True, blank=True, on_delete=models.SET_NULL, related_name="profile_workout")
    meal = models.ForeignKey("MealEntry", null=True, blank=True, on_delete=models.SET_NULL, related_name="profile_meal")
    visibility = models.CharField(max_length=12, choices=VISIBILITY_CHOICES, default="friends")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["-created_at"]


    def __str__(self):
        return f"Post by {self.author.username} @ {self.created_at:%Y-%m-%d %H:%M}"
    
@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(author=instance)

# --- Follow (one-direction) ---
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_relations")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_relations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
        UniqueConstraint(fields=["follower", "following"], name="unique_follow_pair"),
        models.CheckConstraint(check=~models.Q(follower=models.F("following")), name="no_self_follow"),
        ]

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"

# --- Posts ---
class Post(models.Model):
    VISIBILITY_CHOICES = (
    ("friends", "Friends"),
    ("public", "Public"),
    )


    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=2000)
    # Optional attachments to your existing domain objects
    workout = models.ForeignKey("Workout", null=True, blank=True, on_delete=models.SET_NULL, related_name="attached_posts")
    meal = models.ForeignKey("MealEntry", null=True, blank=True, on_delete=models.SET_NULL, related_name="attached_posts")
    visibility = models.CharField(max_length=12, choices=VISIBILITY_CHOICES, default="friends")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.author.username} @ {self.created_at:%Y-%m-%d %H:%M}"

    @property
    def like_count(self):
        return self.likes.count()


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/%Y/%m/")
    alt_text = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Image for Post #{self.post_id}"




class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
        UniqueConstraint(fields=["user", "post"], name="unique_user_post_like"),
        ]

    def __str__(self):
        return f"{self.user.username} ♥ Post {self.post_id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on Post {self.post_id}"
    
# END: SOCIAL_MODELS