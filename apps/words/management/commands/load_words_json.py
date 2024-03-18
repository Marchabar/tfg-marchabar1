import glob
import json
import unicodedata

from django.core.management.base import BaseCommand
from unidecode import unidecode

from apps.videos.models import Video

from ...models import Word


class Command(BaseCommand):
    help = "Load words json"

    def handle(self, *args, **options):
        for filename in glob.glob("answers/*.json"):
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, str):
                    data = json.loads(data)
                words = data.get("used_words")
                for word in words:
                    word = self.first_upper(word)
                    Word.objects.create(
                        word=word,
                        video=Video.objects.get(url=data.get("url")),
                    )

    def first_upper(self, text):
        return text[0].upper() + text[1:]
