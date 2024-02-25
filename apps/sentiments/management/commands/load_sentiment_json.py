import glob
import json

from django.core.management.base import BaseCommand
from unidecode import unidecode

from apps.videos.models import Video

from ...models import Sentiment


class Command(BaseCommand):
    help = "Load sentiment json"

    def handle(self, *args, **options):
        for filename in glob.glob("answers/*.json"):
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                valid_choices = [
                    choice[0]
                    for choice in Sentiment._meta.get_field("sentiment_type").choices
                ]
                # check if for each of the lenguaje in the json, there is a language choice
                for sentiment in data.get("sentiment"):
                    sentiment = unidecode(sentiment.lower())
                    if sentiment not in valid_choices:
                        break
                    elif Sentiment.objects.filter(
                        sentiment_type=sentiment,
                        video=Video.objects.get(url=data.get("url")),
                    ).exists():
                        break
                    else:
                        video = Video.objects.get(url=data.get("url"))
                        Sentiment.objects.create(sentiment_type=sentiment, video=video)
