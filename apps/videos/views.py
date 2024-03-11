from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from apps.topics.models import Topic

# Create your views here.


def get_my_videos(request):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")

    return render(request, "user-videos.html")


def analyze_video_user(request):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")
    top_topics = (
        Topic.objects.values("topic_type")
        .annotate(video_count=Count("video"))
        .order_by("-video_count")[:12]
    )
    top_topics = list(top_topics)

    search = request.GET.get("video-url")
    print(search)

    return render(request, "analysis.html", {"top_topics": top_topics})


def get_videos_by_topic(request, topic_type):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")

    topics = Topic.objects.filter(topic_type=topic_type)
    videos = []
    for topic in topics:
        videos.append(topic.video)

    return render(request, "videos.html", {"videos": videos, "topic_type": topic_type})
