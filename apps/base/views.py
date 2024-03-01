from django.shortcuts import render

from ..languages.models import Language
from ..ratings.models import Rating
from ..sentiments.models import Sentiment
from ..topics.models import Topic
from ..videos.models import Video
from ..words.models import Word


def load_graphs(request):
    videos = Video.objects.all()
    topics = Topic.objects.all()
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
    print(dict_topics)

    return render(
        request,
        "home.html",
        {
            "dict_topics": dict_topics,
        },
    )
