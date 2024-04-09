import json
import os
import re
import traceback
from datetime import datetime

import environ
import openai
import requests
import tiktoken
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from unidecode import unidecode
from youtube_transcript_api import YouTubeTranscriptApi

from apps.languages.management.commands import load_language_json
from apps.languages.models import Language
from apps.sentiments.management.commands import load_sentiment_json
from apps.sentiments.models import Sentiment
from apps.topics.management.commands import load_topics_json
from apps.topics.models import Topic
from apps.videos.models import Video
from apps.words.management.commands import load_words_json
from apps.words.models import Word

from .management.commands import load_video_json

env = environ.Env()
encoding = tiktoken.encoding_for_model("gpt-4")
# Create your views here.


@csrf_exempt
def publish_video(request, video_id):
    video = Video.objects.get(id=video_id)
    video.published = True
    video.save()
    return JsonResponse({"status": "success"})


def all_videos(request):
    # user has to be superuser to access this view
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")
    videos = Video.objects.all().order_by("published")

    if request.user.is_superuser:
        return render(request, "all-videos.html", {"videos": videos})
    else:
        return redirect("/")


def get_video_information(request, video_id):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")

    video = get_object_or_404(Video, id=video_id)
    dict_topics = {}
    topics = Topic.objects.filter(video=video)
    for topic in topics:
        dict_topics[topic.topic_type] = topic.percentage
    sentiments = Sentiment.objects.filter(video=video)
    dict_sentiments = {}
    for sentiment in sentiments:
        if sentiment.sentiment_type not in dict_sentiments:
            dict_sentiments[sentiment.sentiment_type] = 1

    dict_languages = {}
    languages = Language.objects.filter(video=video)
    for language in languages:
        dict_languages[language.language_type] = 1
    dict_words = {}
    words = Word.objects.filter(video=video)
    for word in words:
        dict_words[word.word] = 1
    video_id = extract_video_id(video.url)
    return render(
        request,
        "video-info.html",
        {
            "video": video,
            "video_id": video_id,
            "dict_topics": dict_topics,
            "dict_sentiments": dict_sentiments,
            "dict_languages": dict_languages,
            "dict_words": dict_words,
        },
    )


def analyze_video_user(request):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")

    search = request.GET.get("video-url")

    allowed_channels_ids = {
        "UCPECDsPyGRW5b5E4ibCGhww": "PP",
        "UCB75fTm3weGTmtnitiZcdBw": "PSOE",
        "UCRvpumrJs0qY1xLzeU0Ss1Q": "VOX",
        "UCEg-oyYjgbOL0NG5qjtuRFA": "SUMAR",
    }
    videos = Video.objects.all()

    if search:
        if "youtube.com" not in search and "youtu.be" not in search:
            return render(
                request,
                "analysis.html",
                {"top_topics": top_topics, "message": "La url no es válida."},
            )
        else:
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
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=["es"]
                )
                transcription = " ".join(item["text"] for item in transcript)
                length = video_details.get("length")
                length = convert_duration(length)
                date = video_details.get("date")
                date = format_date(date)
                description = video_details.get("description")
                transcription = f"""
                politician_name = ,
                political_party = {political_party},
                url = {search},
                date = {date},
                length = {length},
                description = {description},
                {transcription}"""
                prompt = general_statement(transcription)
                number_tokens = num_tokens_from_string(prompt, "gpt-4")
                if number_tokens > 2500:
                    return render(
                        request,
                        "analysis.html",
                        {
                            "top_topics": top_topics,
                            "message": "La transcripción es demasiado larga.",
                        },
                    )
                if video_details:
                    response = generate_response(prompt)
                    # response = {
                    #     "politician_name": "Pedro Sánchez",
                    #     "political_party": "PSOE",
                    #     "url": "https://youtu.be/TK8-s7LnX9s?si=X2vDPQbhpMd6AFHc",
                    #     "date": "13/03/2024",
                    #     "length": "02:04",
                    #     "summary": "Pedro Sánchez le pregunta a Feijóo en el Congreso por qué no pide la dimisión de Ayuso, y señala que la respuesta es porque le costaría su puesto en el PP al igual que Casado. También critica la amistad de Feijóo con un capo del narcotráfico en Galicia y señala que en su partido político, Feijóo no hubiera llegado ni a concejal de pueblo.",
                    #     "main_topics": [
                    #         {"Economía": 10},
                    #         {"Salud": 5},
                    #         {"Educación": 5},
                    #         {"Medio ambiente": 0},
                    #         {"Derechos civiles": 0},
                    #         {"Inmigración": 0},
                    #         {"Seguridad nacional": 0},
                    #         {"Política exterior": 0},
                    #         {"Empleo": 5},
                    #         {"Criminalidad": 5},
                    #         {"Impuestos": 0},
                    #         {"Bienestar social": 0},
                    #         {"Tecnología": 0},
                    #         {"Energía": 0},
                    #         {"Vivienda": 0},
                    #         {"Corrupción": 10},
                    #         {"Libertad de prensa": 0},
                    #         {"Igualdad de género": 0},
                    #         {"Diversidad y discriminación": 0},
                    #         {"Pobreza": 0},
                    #         {"Infraestructura": 0},
                    #         {"Religión": 0},
                    #         {"Derechos de las minorías": 0},
                    #         {"Paz y conflicto": 0},
                    #         {"Defensa": 0},
                    #         {"Legislación": 5},
                    #         {"Presupuesto": 0},
                    #         {"Justicia": 5},
                    #         {"ETA": 0},
                    #         {"Historia reciente de España": 0},
                    #         {"Terrorismo": 0},
                    #         {"Acusaciones políticas": 5},
                    #         {"Campaña electoral": 5},
                    #     ],
                    #     "sentiment": ["Enojo", "Frustración", "Desdén", "Empatía"],
                    #     "lenguaje": [
                    #         "Lenguaje formal",
                    #         "Lenguaje retórico",
                    #         "Lenguaje de confrontación",
                    #         "Lenguaje de crítica",
                    #         "Lenguaje de debate",
                    #         "Lenguaje de discurso público",
                    #         "Lenguaje de campaña",
                    #     ],
                    #     "used_words": [
                    #         "dimisión",
                    #         "presidenta",
                    #         "comunidad de Madrid",
                    #         "responsabilidades políticas",
                    #         "ejemplaridad",
                    #         "lucha contra la corrupción",
                    #         "terceras personas",
                    #         "ejercicio",
                    #         "amistad",
                    #         "capo del narcotráfico",
                    #         "Galicia",
                    #         "Canarias",
                    #         "Portugal",
                    #         "Andorra",
                    #         "narcotraficante",
                    #         "blanqueo",
                    #         "21 millones",
                    #         "Francia",
                    #         "diferencia",
                    #         "historial",
                    #         "escalar",
                    #         "partido político",
                    #         "concejal de pueblo",
                    #     ],
                    # }
                    title = video_details.get("title")

                    title = sanitize_filename(video_details.get("title"))

                    root_directory = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), "../..")
                    )

                    # Create the folder named "answers" in the root directory if it doesn't exist
                    answers_folder = os.path.join(root_directory, "answers")
                    if not os.path.exists(answers_folder):
                        os.makedirs(answers_folder)
                    try:
                        # Save the response to a JSON file named after the video title in the "answers" folder
                        with open(
                            os.path.join(answers_folder, f"{title}.json"),
                            "w",
                            encoding="utf-8",
                        ) as file:
                            json.dump(response, file, ensure_ascii=False)

                        # After the file is successfully created, call the load_* functions
                        load_video_json.Command().handle()
                        load_sentiment_json.Command().handle()
                        load_language_json.Command().handle()
                        load_words_json.Command().handle()
                        load_topics_json.Command().handle()
                        # I need to update this video putting the user that is logged in
                        video = Video.objects.get(url=search)
                        video.user = request.user
                        video.save()
                    except Exception as e:
                        print(f"Error creating file: {e}")
                        traceback.print_exc()

                    return redirect("/my-videos")
                else:
                    return render(
                        request,
                        "analysis.html",
                        {"message": "La url no es válida."},
                    )
            else:
                return render(
                    request,
                    "analysis.html",
                    {
                        "message": "La url no es de un canal permitido.",
                    },
                )
    return render(request, "analysis.html")


def top_topics(request):
    top_topics = (
        Topic.objects.values("topic_type")
        .annotate(video_count=Count("video"))
        .order_by("-video_count")[:12]
    )
    top_sentiments = (
        Sentiment.objects.values("sentiment_type")
        .annotate(video_count=Count("video"))
        .order_by("-video_count")[:12]
    )
    top_languages = (
        Language.objects.values("language_type")
        .annotate(video_count=Count("video"))
        .order_by("-video_count")[:12]
    )

    top_topics = list(top_topics)
    top_sentiments = list(top_sentiments)
    top_languages = list(top_languages)

    TOPIC_CHOICES = [
        ("economia", "Economía"),
        ("salud", "Salud"),
        ("educacion", "Educación"),
        ("medio_ambiente", "Medio ambiente"),
        ("derechos_civiles", "Derechos civiles"),
        ("inmigracion", "Inmigración"),
        ("seguridad_nacional", "Seguridad nacional"),
        ("politica_exterior", "Política exterior"),
        ("empleo", "Empleo"),
        ("criminalidad", "Criminalidad"),
        ("impuestos", "Impuestos"),
        ("bienestar_social", "Bienestar social"),
        ("tecnologia", "Tecnología"),
        ("energia", "Energía"),
        ("vivienda", "Vivienda"),
        ("corrupcion", "Corrupción"),
        ("libertad_de_prensa", "Libertad de prensa"),
        ("igualdad_de_genero", "Igualdad de género"),
        ("diversidad_y_discriminacion", "Diversidad y discriminación"),
        ("pobreza", "Pobreza"),
        ("infraestructura", "Infraestructura"),
        ("religion", "Religión"),
        ("derechos_de_las_minorias", "Derechos de las minorías"),
        ("paz_y_conflicto", "Paz y conflicto"),
        ("defensa", "Defensa"),
        ("legislacion", "Legislación"),
        ("presupuesto", "Presupuesto"),
        ("justicia", "Justicia"),
        ("ETA", "ETA"),
        ("historia_reciente_espana", "Historia reciente de España"),
        ("terrorismo", "Terrorismo"),
        ("acusaciones_políticas", "Acusaciones políticas"),
        ("campana_electoral", "Campaña electoral"),
        ("patriotismo", "Patriotismo"),
    ]
    SENTIMENT_CHOICES = [
        ("enojo", "Enojo"),
        ("frustracion", "Frustración"),
        ("pasion", "Pasión"),
        ("entusiasmo", "Entusiasmo"),
        ("preocupacion", "Preocupación"),
        ("confianza", "Confianza"),
        ("desesperacion", "Desesperación"),
        ("optimismo", "Optimismo"),
        ("satisfaccion", "Satisfacción"),
        ("escepticismo", "Escepticismo"),
        ("desden", "Desdén"),
        ("empatia", "Empatía"),
    ]
    LANGUAGE_CHOICES = [
        ("formal", "Lenguaje formal"),
        ("tecnico", "Lenguaje técnico"),
        ("emocional", "Lenguaje emocional"),
        ("persuasivo", "Lenguaje persuasivo"),
        ("retorico", "Lenguaje retórico"),
        ("bipartidista", "Lenguaje bipartidista"),
        ("partidista", "Lenguaje partidista"),
        ("populista", "Lenguaje populista"),
        ("consenso", "Lenguaje de consenso"),
        ("confrontacion", "Lenguaje de confrontación"),
        ("compromiso", "Lenguaje de compromiso"),
        ("promesas", "Lenguaje de promesas"),
        ("critica", "Lenguaje de crítica"),
        ("estadisticas", "Lenguaje de estadísticas"),
        ("datos", "Lenguaje de datos"),
        ("debate", "Lenguaje de debate"),
        ("discurso_publico", "Lenguaje de discurso público"),
        ("campana", "Lenguaje de campaña"),
        ("legislacion", "Lenguaje de legislación"),
        ("negociacion", "Lenguaje de negociación"),
        ("patriótico", "Lenguaje patriótico"),
    ]
    # I need to convert the topic_type to the name of the topic
    for topic in top_topics:
        for choice in TOPIC_CHOICES:
            if choice[0] == topic["topic_type"]:
                topic["topic_type"] = choice[1]
    for sentiment in top_sentiments:
        for choice in SENTIMENT_CHOICES:
            if choice[0] == sentiment["sentiment_type"]:
                sentiment["sentiment_type"] = choice[1]
    for language in top_languages:
        for choice in LANGUAGE_CHOICES:
            if choice[0] == language["language_type"]:
                language["language_type"] = choice[1]

    return render(
        request,
        "top-topics.html",
        {
            "top_topics": top_topics,
            "top_sentiments": top_sentiments,
            "top_languages": top_languages,
        },
    )


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
            description = snippet.get("description")
            return {
                "title": title,
                "thumbnail": thumbnail,
                "channel_id": channel_id,
                "length": length,
                "date": date,
                "description": description,
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


def general_statement(transcription):

    main_topics = [
        "Economía",
        "Salud",
        "Educación",
        "Medio ambiente",
        "Derechos civiles",
        "Inmigración",
        "Seguridad nacional",
        "Política exterior",
        "Empleo",
        "Criminalidad",
        "Impuestos",
        "Bienestar social",
        "Tecnología",
        "Energía",
        "Vivienda",
        "Corrupción",
        "Libertad de prensa",
        "Igualdad de género",
        "Diversidad y discriminación",
        "Pobreza",
        "Infraestructura",
        "Religión",
        "Derechos de las minorías",
        "Paz y conflicto",
        "Defensa",
        "Legislación",
        "Presupuesto",
        "Justicia",
        "ETA",
        "Historia reciente de España",
        "Terrorismo",
        "Acusaciones políticas",
        "Campaña electoral",
    ]

    sentiment = [
        "Enojo",
        "Frustración",
        "Pasión",
        "Entusiasmo",
        "Preocupación",
        "Confianza",
        "Desesperación",
        "Optimismo",
        "Satisfacción",
        "Escepticismo",
        "Desdén",
        "Empatía",
    ]

    lenguaje = [
        "Lenguaje formal",
        "Lenguaje técnico",
        "Lenguaje emocional",
        "Lenguaje persuasivo",
        "Lenguaje retórico",
        "Lenguaje bipartidista",
        "Lenguaje partidista",
        "Lenguaje populista",
        "Lenguaje de consenso",
        "Lenguaje de confrontación",
        "Lenguaje de compromiso",
        "Lenguaje de promesas",
        "Lenguaje de crítica",
        "Lenguaje de estadísticas",
        "Lenguaje de datos",
        "Lenguaje de debate",
        "Lenguaje de discurso público",
        "Lenguaje de campaña",
        "Lenguaje de legislación",
        "Lenguaje de negociación",
    ]

    prompt = f"""Analiza las siguientes transcripciones de textos de políticos, y respóndeme a las preguntas que te propongo en formato json. Las claves del formato json son politician_name, political_party, date, length, summary, main_topics, sentiment, lenguaje y used_words. Para sus valores es muy importante que tengas en cuenta las siguientes condiciones : 
    Para la key main_topics solo pueden ser valores que se encuentren en el siguiente array. Para esta key,necesito un diccionario que contenga el main_topic y el porcentaje del que se habla de el. {main_topics}
    Para la key sentiment solo puede ser uno o varios de los siguientes array. Esto significa que aunque encuentres otros sentiments, solo debes coger los que esten en este array: {sentiment}. 
    Para la key lenguaje solo puede ser uno o varios de los siguientes array. Esto significa que aunque encuentres otros lenguajes, solo debes coger los que esten en este array:  {lenguaje}. 
    Para la key used_words coge las palabras politicas que mas se usen durante la transcripción. 
    Para la key politician_name (nombre del político) tienes que sacarlo del title o description del video (sino sacas el politican_name pon Político no reconocido)
    La transcripción es la siguiente, y ya contiene el partido al que pertenece, la url, la fecha, y la duracion. Esto tambien tienes que incluirlo en el json que me das como respuesta. Además tienes que incluir un resumen corto en un párrafo de la transcripcion para la key summary. Recuerda tener en cuenta las limitaciones y solo coger valores de los arrays para las keys que lo necesitan: {transcription}
    """
    return prompt


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def generate_response(
    prompt,
    temperature=0.2,
    max_tokens=1500,
):
    openai.api_key = env("OPENAI_API_KEY")
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].text.strip()


def sanitize_filename(filename):
    filename = unidecode(filename)  # Remove accents
    filename = filename.lower()  # Convert to lowercase
    filename = filename.replace(" ", "_")  # Replace spaces with underscores
    return re.sub(r'[\\/*?:"<>|]', "", filename)  # Remove invalid characters


def get_videos_by_topic(request, topic_type):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")

    topics = Topic.objects.filter(topic_type=topic_type)
    videos = []
    for topic in topics:
        if topic.video.published:
            videos.append(topic.video)
    TOPIC_CHOICES = [
        ("economia", "Economía"),
        ("salud", "Salud"),
        ("educacion", "Educación"),
        ("medio_ambiente", "Medio ambiente"),
        ("derechos_civiles", "Derechos civiles"),
        ("inmigracion", "Inmigración"),
        ("seguridad_nacional", "Seguridad nacional"),
        ("politica_exterior", "Política exterior"),
        ("empleo", "Empleo"),
        ("criminalidad", "Criminalidad"),
        ("impuestos", "Impuestos"),
        ("bienestar_social", "Bienestar social"),
        ("tecnologia", "Tecnología"),
        ("energia", "Energía"),
        ("vivienda", "Vivienda"),
        ("corrupcion", "Corrupción"),
        ("libertad_de_prensa", "Libertad de prensa"),
        ("igualdad_de_genero", "Igualdad de género"),
        ("diversidad_y_discriminacion", "Diversidad y discriminación"),
        ("pobreza", "Pobreza"),
        ("infraestructura", "Infraestructura"),
        ("religion", "Religión"),
        ("derechos_de_las_minorias", "Derechos de las minorías"),
        ("paz_y_conflicto", "Paz y conflicto"),
        ("defensa", "Defensa"),
        ("legislacion", "Legislación"),
        ("presupuesto", "Presupuesto"),
        ("justicia", "Justicia"),
        ("ETA", "ETA"),
        ("historia_reciente_espana", "Historia reciente de España"),
        ("terrorismo", "Terrorismo"),
        ("acusaciones_políticas", "Acusaciones políticas"),
        ("campana_electoral", "Campaña electoral"),
        ("patriotismo", "Patriotismo"),
    ]

    for choice in TOPIC_CHOICES:
        if choice[0] == topic_type:
            topic_type = choice[1]

    return render(
        request, "videos-topic.html", {"videos": videos, "topic_type": topic_type}
    )


def get_videos_by_user(request):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")

    # I need to get the videos which user is the one that is logged in
    user_videos = Video.objects.filter(user=request.user)

    return render(request, "user-videos.html", {"user_videos": user_videos})
