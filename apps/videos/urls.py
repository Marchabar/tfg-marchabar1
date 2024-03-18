from django.urls import path
from django.urls.conf import include

from apps.videos import views

urlpatterns = [
    path("analysis", views.analyze_video_user, name="analysis"),
    path("topics/<str:topic_type>", views.get_videos_by_topic, name="topic"),
    path("my-videos", views.get_videos_by_user, name="my-videos"),
    path(
        "videos/<int:video_id>",
        views.get_video_information,
        name="video",
    ),
    path("all-videos", views.all_videos, name="all-videos"),
    path("publish-video/<int:video_id>", views.publish_video, name="publish_video"),
]
