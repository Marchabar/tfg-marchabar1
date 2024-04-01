import glob
import json

from django.core.management.base import BaseCommand
from unidecode import unidecode

from apps.videos.models import Video

from ...models import Language


class Command(BaseCommand):
    help = "Load language json"

    def handle(self, *args, **options):
        for filename in glob.glob("answers/*.json"):
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, str):
                    data = json.loads(data)
                valid_choices = [
                    choice[0]
                    for choice in Language._meta.get_field("language_type").choices
                ]
                # check if for each of the lenguaje in the json, there is a language choice
                for lenguaje in data.get("lenguaje"):
                    lenguaje = unidecode(lenguaje.lower()).split()[-1]
                    if lenguaje not in valid_choices:
                        break
                    elif Language.objects.filter(
                        language_type=lenguaje,
                        video=Video.objects.get(url=data.get("url")),
                    ).exists():
                        break
                    else:
                        video = Video.objects.get(url=data.get("url"))
                        Language.objects.create(language_type=lenguaje, video=video)
