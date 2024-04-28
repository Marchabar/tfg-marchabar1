import glob
import json

from django.core.management.base import BaseCommand

from ...models import Falacy


class Command(BaseCommand):
    help = "Load language json"

    def handle(self, *args, **options):
        for filename in glob.glob("falacies_json/*.json"):
            with open(filename, "r", encoding="utf-8") as file:
                if file.read().strip():  # Check if file is not empty
                    file.seek(0)  # Reset file position to the beginning
                    data = json.load(file)
                    if data:
                        if not Falacy.objects.filter(title=data["title"]).exists():
                            Falacy.objects.create(
                                title=data["title"],
                                politician=data["politician"],
                                political_party=data["political_party"],
                                argument=data["argument"],
                                image=data["image"],
                            )
