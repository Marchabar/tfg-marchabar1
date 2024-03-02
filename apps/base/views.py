from django.shortcuts import render

from ..languages.models import Language
from ..ratings.models import Rating
from ..sentiments.models import Sentiment
from ..topics.models import Topic
from ..videos.models import Video
from ..words.models import Word


def load_charts(request):
    videos = Video.objects.all()
    topics = Topic.objects.all()
    sentiments = Sentiment.objects.all()
    dict_topics = {}

    for video in videos:
        if video.political_party not in dict_topics:
            dict_topics[video.political_party] = {}
        for topic in topics:
            if topic.video.id != video.id:
                continue
            else:
                if topic.topic_type not in dict_topics[video.political_party]:
                    dict_topics[video.political_party][topic.topic_type] = 0
                dict_topics[video.political_party][topic.topic_type] += topic.percentage

    for party in dict_topics:
        total = sum(dict_topics[party].values())
        for topic in dict_topics[party]:
            dict_topics[party][topic] = round(
                dict_topics[party][topic] / total * 100, 2
            )

    for party in dict_topics:
        dict_topics[party] = str(dict_topics[party]).replace("'", '"')

    dict_sentiments = {}
    for video in videos:
        if video.political_party not in dict_sentiments:
            dict_sentiments[video.political_party] = []
        for sentiment in sentiments:
            if sentiment.video.id != video.id:
                continue
            else:
                if (
                    sentiment.sentiment_type
                    not in dict_sentiments[video.political_party]
                ):
                    dict_sentiments[video.political_party].append(
                        sentiment.sentiment_type
                    )
    for party in dict_sentiments:
        dict_sentiments[party] = str(dict_sentiments[party]).replace("'", '"')

    # I want to order videos by date
    videos = Video.objects.all().order_by("date")[:3]

    return render(
        request,
        "home.html",
        {
            "dict_topics": dict_topics,
            "dict_sentiments": dict_sentiments,
            "videos": videos,
        },
    )
