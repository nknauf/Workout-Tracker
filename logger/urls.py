from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# BEGIN: APP_URLS
urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('create-workout/', views.create_workout, name='create_workout'),
    path('ai-create-workout/', views.ai_create_workout, name='ai_create_workout'),
    path('exercises/', views.exercises, name="exercises"),
    path("delete-meal/<int:meal_id>/", views.delete_meal_log, name="delete_meal_log"),

    # newly created
    path("u/<str:username>/", views.profile, name="profile"),
    path("progress/", views.progress, name="progress"),
    path("api/daily/today/", views.daily_today, name="daily_today"),
    
    # API endpoints for n8n integration
    path('api/trigger-workout-agent/', views.trigger_workout_agent, name='trigger_workout_agent'),
    path('api/create-workout-from-agent/', views.create_workout_from_agent, name='create_workout_from_agent'),
    path('api/recent-workouts/', views.get_recent_workouts, name='get_recent_workouts'),

    # social media views
    path("social/", views.social_feed, name="social_feed"),
    path("social/post/new/", views.create_post, name="create_post"),
    path("social/post/<int:pk>/", views.post_detail, name="post_detail"),
    path("social/post/<int:pk>/like/", views.toggle_like, name="toggle_like"),
    path("social/post/<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("u/<str:username>/", views.profile, name="profile"),
    path("u/<str:username>/follow/", views.toggle_follow, name="toggle_follow"),
    path("social/repdeck/", views.repdeck_view, name="repdeck_view"),
    path("api/posts/", views.posts_api, name="posts_api"),
]
# END: APP_URLS

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)