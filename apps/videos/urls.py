from django.urls import path
from django.urls.conf import include

from apps.videos import views

urlpatterns = [
    path("analysis", views.analyze_video_user, name="analysis"),
    path("videos/<str:topic_type>", views.get_videos_by_topic, name="topic"),
]
