from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from apps.topics.models import Topic

# Create your views here.


def analizar_video_usuario(request):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")
    # I need to get the 8 topics that appear in more videos taking into account a Topic has a video, a percentage and a topic_type
    top_topics = (
        Topic.objects.values("topic_type")
        .annotate(video_count=Count("video"))
        .order_by("-video_count")[:12]
    )
    top_topics = list(top_topics)

    return render(request, "analysis.html", {"top_topics": top_topics})
