import heapq
import json
from collections import defaultdict

from django.shortcuts import render

from ..languages.models import Language
from ..ratings.models import Rating
from ..sentiments.models import Sentiment
from ..topics.models import Topic
from ..videos.models import Video
from ..words.models import Word


def load_general(request):
    videos = Video.objects.filter(published=True)
    dict_general = defaultdict(
        lambda: {
            "topics": defaultdict(int),
            "sentiments": defaultdict(int),
            "languages": defaultdict(int),
        }
    )

    for video in videos:
        party = video.political_party

        # Count topics
        topics = Topic.objects.filter(video=video)
        for topic in topics:
            if topic.topic_type not in dict_general[party]["topics"]:
                dict_general[party]["topics"][topic.topic_type] = 0
            dict_general[party]["topics"][topic.topic_type] += topic.percentage

        # Count sentiments
        sentiments = Sentiment.objects.filter(video=video)
        for sentiment in sentiments:
            dict_general[party]["sentiments"][sentiment.sentiment_type] += 1

        # Count languages
        languages = Language.objects.filter(video=video)
        for language in languages:
            dict_general[party]["languages"][language.language_type] += 1

    # Iterate through each party
    for party, values in dict_general.items():
        total_percentage_topics = sum(
            values["topics"].values()
        )  # Calculate total percentage for the party

        top_sentiments = heapq.nlargest(
            6, values["sentiments"], key=values["sentiments"].get
        )

        top_languages = heapq.nlargest(
            6, values["languages"], key=values["languages"].get
        )
        # Get the top 6 topics with highest percentages
        top_topics = heapq.nlargest(6, values["topics"], key=values["topics"].get)

        # Calculate the sum of percentages of topics not in top 6
        rest_percentage_topics = sum(
            percentage
            for topic, percentage in values["topics"].items()
            if topic not in top_topics
        )

        rest_count_sentiments = sum(
            count
            for sentiment, count in values["sentiments"].items()
            if sentiment not in top_sentiments
        )

        rest_count_languages = sum(
            count
            for language, count in values["languages"].items()
            if language not in top_languages
        )

        # Calculate percentage for each topic based on the total percentage
        for topic, percentage in values["topics"].items():
            values["topics"][topic] = round(
                (percentage / total_percentage_topics) * 100, 2
            )

        values["sentiments"]["Otros"] = rest_count_sentiments

        values["languages"]["Otros"] = rest_count_languages

        values["topics"]["Otros"] = round(
            rest_percentage_topics / total_percentage_topics * 100, 2
        )

        topics_to_remove = [
            topic
            for topic in values["topics"]
            if topic not in top_topics and topic != "Otros"
        ]
        sentiments_to_remove = [
            sentiment
            for sentiment in values["sentiments"]
            if sentiment not in top_sentiments and sentiment != "Otros"
        ]

        languages_to_remove = [
            language
            for language in values["languages"]
            if language not in top_languages and language != "Otros"
        ]

        # Remove topics not in top 6
        for topic in topics_to_remove:
            del values["topics"][topic]

        for sentiment in sentiments_to_remove:
            del values["sentiments"][sentiment]

        for language in languages_to_remove:
            del values["languages"][language]

    # Convert defaultdict to dict
    dict_general = {k: dict(v) for k, v in dict_general.items()}

    # Convert to JSON
    dict_general_json = json.dumps(dict_general)

    mapping_dict = {
        "economia": "Economía",
        "salud": "Salud",
        "educacion": "Educación",
        "medio_ambiente": "Medio ambiente",
        "derechos_civiles": "Derechos civiles",
        "inmigracion": "Inmigración",
        "seguridad_nacional": "Seguridad nacional",
        "politica_exterior": "Política exterior",
        "empleo": "Empleo",
        "criminalidad": "Criminalidad",
        "impuestos": "Impuestos",
        "bienestar_social": "Bienestar social",
        "tecnologia": "Tecnología",
        "energia": "Energía",
        "vivienda": "Vivienda",
        "corrupcion": "Corrupción",
        "libertad_de_prensa": "Libertad de prensa",
        "igualdad_de_genero": "Igualdad de género",
        "diversidad_y_discriminacion": "Diversidad y discriminación",
        "pobreza": "Pobreza",
        "infraestructura": "Infraestructura",
        "religion": "Religión",
        "derechos_de_las_minorias": "Derechos de las minorías",
        "paz_y_conflicto": "Paz y conflicto",
        "defensa": "Defensa",
        "legislacion": "Legislación",
        "presupuesto": "Presupuesto",
        "justicia": "Justicia",
        "eta": "ETA",
        "historia_reciente_de_espana": "Historia reciente de España",
        "terrorismo": "Terrorismo",
        "acusaciones_politicas": "Acusaciones políticas",
        "campana_electoral": "Campaña electoral",
        "enojo": "Enojo",
        "frustracion": "Frustración",
        "pasion": "Pasión",
        "entusiasmo": "Entusiasmo",
        "preocupacion": "Preocupación",
        "confianza": "Confianza",
        "desesperacion": "Desesperación",
        "optimismo": "Optimismo",
        "satisfaccion": "Satisfacción",
        "escepticismo": "Escepticismo",
        "desden": "Desdén",
        "empatia": "Empatía",
        "formal": "Formal",
        "tecnico": "Técnico",
        "emocional": "Emocional",
        "persuasivo": "Persuasivo",
        "retorico": "Retórico",
        "bipartidista": "Bipartidista",
        "partidista": "Partidista",
        "populista": "Populista",
        "confrontacion": "Confrontación",
        "consenso": "Consenso",
        "compromiso": "Compromiso",
        "promesas": "Promesas",
        "critica": "Crítica",
        "estadisticas": "Estadísticas",
        "datos": "Datos",
        "debate": "Debate",
        "discurso_publico": "Discurso público",
        "campana": "Campaña",
        "legislacion": "Legislación",
        "negociacion": "Negociación",
    }

    PARTIES = ["PP", "PSOE", "VOX", "SUMAR"]

    words = Word.objects.select_related("video").filter(
        video__political_party__in=PARTIES
    )

    # Initialize the dictionary
    dict_words = defaultdict(lambda: defaultdict(int))

    # Count words per party
    for word in words:
        dict_words[word.video.political_party][word.word] += 1

    dict_words = {k: dict(v) for k, v in dict_words.items()}

    dict_general = json.loads(dict_general_json)

    for party in dict_general:
        for category in ["topics", "sentiments", "languages"]:
            items = {
                mapping_dict.get(k, k): v
                for k, v in dict_general[party][category].items()
                if k != "Otros"
            }
            sorted_items = sorted(items.items(), key=lambda x: (-x[1], x[0]))
            dict_general[party][category] = dict(sorted_items[:5])

        words_items = dict_words[party].items()
        sorted_words_items = sorted(words_items, key=lambda x: (-x[1], x[0]))
        dict_general[party]["words"] = dict(sorted_words_items[:5])

    return render(
        request,
        "general.html",
        {"dict_general": dict_general_json, "dict_general_table": dict_general},
    )


def load_politician(request):
    videos = Video.objects.filter(published=True)
    dict_politicians = {}
    for video in videos:
        if video.politician_name not in dict_politicians:
            dict_politicians[video.politician_name] = [video]
        else:
            dict_politicians[video.politician_name].append(video)

    dict_politicians = dict(sorted(dict_politicians.items()))

    if "Político no reconocido" in dict_politicians:
        dict_politicians.pop("Político no reconocido")

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

    for politician, values in dict_topics.items():
        total_percentage = sum(values.values())

        top_topics = heapq.nlargest(6, values, key=values.get)

        rest_percentage = sum(
            percentage
            for topic, percentage in values.items()
            if topic not in top_topics
        )

        for topic, percentage in values.items():
            values[topic] = round((percentage / total_percentage) * 100, 2)

        values["Otros"] = round(rest_percentage / total_percentage * 100, 2)

        topics_to_remove = [
            topic for topic in values if topic not in top_topics and topic != "Otros"
        ]

        for topic in topics_to_remove:
            del values[topic]

        dict_topics[politician] = str(dict_topics[politician]).replace("'", '"')

    dict_sentiments = {}
    for video in videos:
        if video.politician_name not in dict_sentiments:
            dict_sentiments[video.politician_name] = {}
        for sentiment in sentiments:
            if sentiment.video.id != video.id:
                continue
            else:
                if (
                    sentiment.sentiment_type
                    not in dict_sentiments[video.politician_name]
                ):
                    dict_sentiments[video.politician_name][sentiment.sentiment_type] = 1
                else:
                    dict_sentiments[video.politician_name][
                        sentiment.sentiment_type
                    ] += 1

    for party, values in dict_sentiments.items():
        top_sentiments = heapq.nlargest(6, values, key=values.get)

        rest_count = sum(
            count
            for sentiment, count in values.items()
            if sentiment not in top_sentiments
        )

        values["Otros"] = rest_count

        sentiments_to_remove = [
            sentiment
            for sentiment in values
            if sentiment not in top_sentiments and sentiment != "Otros"
        ]

        for sentiment in sentiments_to_remove:
            del values[sentiment]

        dict_sentiments[party] = str(values).replace("'", '"')

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

    for party, values in dict_languages.items():
        top_languages = heapq.nlargest(6, values, key=values.get)

        rest_count = sum(
            count for language, count in values.items() if language not in top_languages
        )

        values["Otros"] = rest_count

        languages_to_remove = [
            language
            for language in values
            if language not in top_languages and language != "Otros"
        ]

        for language in languages_to_remove:
            del values[language]

        dict_languages[party] = str(values).replace("'", '"')

    politicians = Video.objects.values_list("politician_name", flat=True).distinct()
    videos = Video.objects.filter(published=True).order_by("-date")[:3]
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

    for party, values in dict_topics.items():
        total_percentage = sum(values.values())

        top_topics = heapq.nlargest(6, values, key=values.get)

        rest_percentage = sum(
            percentage
            for topic, percentage in values.items()
            if topic not in top_topics
        )

        for topic, percentage in values.items():
            values[topic] = round((percentage / total_percentage) * 100, 2)

        values["Otros"] = round(rest_percentage / total_percentage * 100, 2)

        topics_to_remove = [
            topic for topic in values if topic not in top_topics and topic != "Otros"
        ]

        for topic in topics_to_remove:
            del values[topic]

        dict_topics[party] = str(dict_topics[party]).replace("'", '"')

    dict_sentiments = {}
    for video in videos:
        if video.political_party not in dict_sentiments:
            dict_sentiments[video.political_party] = {}
        for sentiment in sentiments:
            if sentiment.video.id != video.id:
                continue
            else:
                if (
                    sentiment.sentiment_type
                    not in dict_sentiments[video.political_party]
                ):
                    dict_sentiments[video.political_party][sentiment.sentiment_type] = 1
                else:
                    dict_sentiments[video.political_party][
                        sentiment.sentiment_type
                    ] += 1

    for party, values in dict_sentiments.items():
        top_sentiments = heapq.nlargest(6, values, key=values.get)

        rest_count = sum(
            count
            for sentiment, count in values.items()
            if sentiment not in top_sentiments
        )

        values["Otros"] = rest_count

        sentiments_to_remove = [
            sentiment
            for sentiment in values
            if sentiment not in top_sentiments and sentiment != "Otros"
        ]

        for sentiment in sentiments_to_remove:
            del values[sentiment]

        dict_sentiments[party] = str(values).replace("'", '"')

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

    for party, values in dict_languages.items():
        top_languages = heapq.nlargest(6, values, key=values.get)

        rest_count = sum(
            count for language, count in values.items() if language not in top_languages
        )

        values["Otros"] = rest_count

        languages_to_remove = [
            language
            for language in values
            if language not in top_languages and language != "Otros"
        ]

        for language in languages_to_remove:
            del values[language]

        dict_languages[party] = str(values).replace("'", '"')

    videos = Video.objects.filter(published=True).order_by("-date")[:3]
    PARTIES = ["PP", "PSOE", "VOX", "SUMAR"]

    words = Word.objects.select_related("video").filter(
        video__political_party__in=PARTIES
    )

    # Initialize the dictionary
    dict_words = defaultdict(lambda: defaultdict(int))

    # Count words per party
    for word in words:
        dict_words[word.video.political_party][word.word] += 1

    dict_words = {k: dict(v) for k, v in dict_words.items()}

    # Convert dictionary to JSON
    dict_words = json.dumps(dict_words)

    return render(
        request,
        "home.html",
        {
            "dict_topics": dict_topics,
            "dict_sentiments": dict_sentiments,
            "dict_languages": dict_languages,
            "videos": videos,
            "dict_words": dict_words,
        },
    )
