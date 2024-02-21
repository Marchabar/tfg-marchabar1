import json

from django.core.management.base import BaseCommand
from languages.models import Language


class Command(BaseCommand):
    help = "Load language json"

    def handle(self, *args, **options):
        for filename in glob.glob("answers/*.json"):
            with open(filename, "r") as file:
                data = json.load(file)
                valid_choices = [
                    choice[0]
                    for choice in Language._meta.get_field("language_type").choices
                ]
                for answer in data:
                    # check if for each of the lenguaje in the json, there is a language choice
                    for lenguaje in answer["lenguaje"]:
                        if lenguaje not in valid_choices:
                            break
                        else:
                            # get the url in the json and get the id of the video which has already been created containing this url
                            video_id = Video.objects.get(url=answer["url"]).id
                            # create a new language object
                            Language.objects.create(
                                language_type=lenguaje, video=video_id
                            )
