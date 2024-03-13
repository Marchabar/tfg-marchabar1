import json
import os
import re
from datetime import datetime

import environ
import openai
import requests
import tiktoken
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render
from unidecode import unidecode
from youtube_transcript_api import YouTubeTranscriptApi

from apps.languages.management.commands import load_language_json
from apps.sentiments.management.commands import load_sentiment_json
from apps.topics.management.commands import load_topics_json
from apps.topics.models import Topic
from apps.videos.models import Video
from apps.words.management.commands import load_words_json

from .management.commands import load_video_json

env = environ.Env()
encoding = tiktoken.encoding_for_model("gpt-4")
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
                    print(response)
                    # response = {
                    #     "politician_name": "Alberto Núñez Feijóo",
                    #     "political_party": "PP",
                    #     "url": "https://www.youtube.com/watch?v=n57eQqB5NEM",
                    #     "date": "13/02/2024",
                    #     "length": "01:06",
                    #     "summary": "Durante la campaña de las elecciones al parlamento gallego, Alberto Núñez Feijóo, del Partido Popular, defiende la postura a favor del Estado de Derecho y la Igualdad de todos los españoles desde Galicia.",
                    #     "main_topics": {
                    #         "Derechos civiles": 10,
                    #         "Política exterior": 5,
                    #         "Inmigración": 5,
                    #         "Campaña electoral": 10,
                    #     },
                    #     "sentiment": ["Escepticismo", "Desdén"],
                    #     "lenguaje": ["Lenguaje formal", "Lenguaje de campaña"],
                    #     "used_words": [
                    #         "amnistía",
                    #         "ilegal",
                    #         "inconstitucional",
                    #         "igualdad",
                    #         "indulto",
                    #         "independentismo",
                    #         "Sánchez",
                    #         "mal gobierno",
                    #         "buen gobierno",
                    #         "desgobierno",
                    #         "experiencia",
                    #         "gobernar",
                    #         "papeleta",
                    #         "partido popular",
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
                    except Exception as e:
                        print(f"Error creating file: {e}")

                    return redirect("/my-videos")
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
    Para la key main_topics solo y solo si, pueden ser valores que se encuentren en el siguiente array. Esto significa que aunque encuentres otros main_topics, solo debes coger los que esten en este array y sean mas similares a los que has encontrado.     Recuerda que los valores ademas tienen que tener un porcentaje que corresponda al tiempo que se habla de ellos en la transcripción {main_topics}
    Para la key sentiment solo puede ser uno o varios de los siguientes array. Esto significa que aunque encuentres otros sentiments, solo debes coger los que esten en este array: {sentiment}. 
    Para la key lenguaje solo puede ser uno o varios de los siguientes array. Esto significa que aunque encuentres otros lenguajes, solo debes coger los que esten en este array:  {lenguaje}. 
    Para la key used_words coge las palabras politicas que mas se usen durante la transcripción. 
    Para la key politician_name (nombre del político) tienes que intentar sacarlo del title o description (sino sacas el politican_name pon Político no reconocido)
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

    return render(request, "videos.html", {"videos": videos, "topic_type": topic_type})
