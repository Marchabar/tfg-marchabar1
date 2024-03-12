import re
from datetime import datetime

import environ
import requests
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render
from youtube_transcript_api import YouTubeTranscriptApi

from apps.topics.models import Topic
from apps.videos.models import Video

env = environ.Env()

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

    allowed_channels_ids = {
        "UCPECDsPyGRW5b5E4ibCGhww": "PP",
        "UCB75fTm3weGTmtnitiZcdBw": "PSOE",
        "UCRvpumrJs0qY1xLzeU0Ss1Q": "VOX",
        "UCEg-oyYjgbOL0NG5qjtuRFA": "SUMAR",
    }
    videos = Video.objects.all()

    if search:
        for video in videos:
            if video.url == search:
                return render(
                    request,
                    "analysis.html",
                    {
                        "top_topics": top_topics,
                        "message": "Este vídeo ya ha sido analizado.",
                    },
                )
        video_id = extract_video_id(search)
        video_details = get_video_details(video_id)
        channel_id = video_details.get("channel_id")
        if channel_id in allowed_channels_ids:
            political_party = allowed_channels_ids[channel_id]
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["es"])
            transcription = " ".join(item["text"] for item in transcript)
            length = video_details.get("length")
            length = convert_duration(length)
            date = video_details.get("date")
            date = format_date(date)
            transcription = f"""
            politician_name = 
            political_party = {political_party}
            url = {search}
            date = {date}
            length = {length}
            {transcription}"""
            print(transcription)
            if video_details:
                title = video_details.get("title")
                thumbnail = video_details.get("thumbnail")
                return render(
                    request,
                    "analysis.html",
                    {
                        "top_topics": top_topics,
                        "video_id": video_id,
                        "title": title,
                        "thumbnail": thumbnail,
                    },
                )
            else:
                return render(
                    request,
                    "analysis.html",
                    {"top_topics": top_topics, "message": "La url no es válida."},
                )
        else:
            return render(
                request,
                "analysis.html",
                {
                    "top_topics": top_topics,
                    "message": "La url no es de un canal permitido.",
                },
            )
    return render(request, "analysis.html", {"top_topics": top_topics})


def extract_video_id(video_url):
    match = re.search(
        r'(?:youtu\.be\/|youtube\.com\/(?:.*\/v\/|.*[?&]v=|.*[?&]vi=))([^"&?\/\s]{11})',
        video_url,
    )
    if match:
        return match.group(1)
    return None


def get_video_details(video_id):
    youtube_api_key = env("YOUTUBE_API_KEY")
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={youtube_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and data["items"]:
            snippet = data["items"][0]["snippet"]
            content_details = data["items"][0].get("contentDetails", {})
            title = snippet.get("title")
            thumbnail = snippet.get("thumbnails").get("default").get("url")
            channel_id = snippet.get("channelId")
            length = content_details.get("duration")
            date = snippet.get("publishedAt")
            return {
                "title": title,
                "thumbnail": thumbnail,
                "channel_id": channel_id,
                "length": length,
                "date": date,
            }
    return None


def convert_duration(duration):
    # Match and extract hours, minutes and seconds
    match = re.match("PT(\d+H)?(\d+M)?(\d+S)?", duration)
    hours_str = match.group(1) if match.group(1) else "0H"
    minutes_str = match.group(2) if match.group(2) else "0M"
    seconds_str = match.group(3) if match.group(3) else "0S"

    # Remove the letters and convert to integers
    hours = int(hours_str[:-1])
    minutes = int(minutes_str[:-1])
    seconds = int(seconds_str[:-1])

    # Convert the duration to minutes and seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds
    minutes, seconds = divmod(total_seconds, 60)

    # Return the duration in the format 'MM:SS'
    return f"{int(minutes):02d}:{int(seconds):02d}"


def format_date(date_str):
    # Parse the date
    date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

    # Format the date
    formatted_date = date.strftime("%d/%m/%Y")

    return formatted_date


def get_videos_by_topic(request, topic_type):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")

    topics = Topic.objects.filter(topic_type=topic_type)
    videos = []
    for topic in topics:
        if topic.video.published:
            videos.append(topic.video)

    return render(request, "videos.html", {"videos": videos, "topic_type": topic_type})
