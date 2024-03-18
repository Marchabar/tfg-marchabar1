from django.shortcuts import render

from ..languages.models import Language
from ..ratings.models import Rating
from ..sentiments.models import Sentiment
from ..topics.models import Topic
from ..videos.models import Video
from ..words.models import Word


def load_politician(request):
    videos = Video.objects.filter(published=True)
    dict_politicians = {}
    for video in videos:
        if video.politician_name not in dict_politicians:
            dict_politicians[video.politician_name] = [video]
        else:
            dict_politicians[video.politician_name].append(video)
    # I want to order dict_politicians by the key in alphabetic order
    dict_politicians = dict(sorted(dict_politicians.items()))

    sentiments = Sentiment.objects.all()
    languages = Language.objects.all()
    topics = Topic.objects.all()
    dict_topics = {}
    for video in videos:
        if video.politician_name not in dict_topics:
            dict_topics[video.politician_name] = {}
        for topic in topics:
            if topic.video.id != video.id:
                continue
            else:
                if topic.topic_type not in dict_topics[video.politician_name]:
                    dict_topics[video.politician_name][topic.topic_type] = 0
                dict_topics[video.politician_name][topic.topic_type] += topic.percentage

    for politician in dict_topics:
        total = sum(dict_topics[politician].values())
        for topic in dict_topics[politician]:
            dict_topics[politician][topic] = round(
                dict_topics[politician][topic] / total * 100, 2
            )

    for politician in dict_topics:
        dict_topics[politician] = str(dict_topics[politician]).replace("'", '"')

    dict_sentiments = {}
    for video in videos:
        if video.politician_name not in dict_sentiments:
            dict_sentiments[video.politician_name] = []
        for sentiment in sentiments:
            if sentiment.video.id != video.id:
                continue
            else:
                if (
                    sentiment.sentiment_type
                    not in dict_sentiments[video.politician_name]
                ):
                    dict_sentiments[video.politician_name].append(
                        sentiment.sentiment_type
                    )

    for politician in dict_sentiments:
        dict_sentiments[politician] = str(dict_sentiments[politician]).replace("'", '"')

    dict_languages = {}
    for video in videos:
        if video.politician_name not in dict_languages:
            dict_languages[video.politician_name] = {}
        for language in languages:
            if language.video.id != video.id:
                continue
            else:
                if language.language_type not in dict_languages[video.politician_name]:
                    dict_languages[video.politician_name][language.language_type] = 0
                dict_languages[video.politician_name][language.language_type] += 1
    for poltician in dict_languages:
        dict_languages[politician] = str(dict_languages[politician]).replace("'", '"')

    politicians = Video.objects.values_list("politician_name", flat=True).distinct()
    videos = Video.objects.all().order_by("date")[:3]
    print(dict_sentiments)
    return render(
        request,
        "politician.html",
        {
            "dict_politicians": dict_politicians,
            "dict_sentiments": dict_sentiments,
            "dict_languages": dict_languages,
            "dict_topics": dict_topics,
            "politicians": politicians,
            "videos": videos,
        },
    )


def load_charts(request):
    videos = Video.objects.filter(published=True)
    topics = Topic.objects.all()
    sentiments = Sentiment.objects.all()
    languages = Language.objects.all()
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

    dict_languages = {}
    for video in videos:
        if video.political_party not in dict_languages:
            dict_languages[video.political_party] = {}
        for language in languages:
            if language.video.id != video.id:
                continue
            else:
                if language.language_type not in dict_languages[video.political_party]:
                    dict_languages[video.political_party][language.language_type] = 0
                dict_languages[video.political_party][language.language_type] += 1
    for party in dict_languages:
        dict_languages[party] = str(dict_languages[party]).replace("'", '"')

    videos = Video.objects.all().order_by("date")[:3]

    return render(
        request,
        "home.html",
        {
            "dict_topics": dict_topics,
            "dict_sentiments": dict_sentiments,
            "dict_languages": dict_languages,
            "videos": videos,
        },
    )
