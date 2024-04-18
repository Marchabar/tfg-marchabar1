import glob
import json
import unicodedata

from django.core.management.base import BaseCommand
from unidecode import unidecode

from apps.videos.models import Video

from ...models import Topic


class Command(BaseCommand):
    help = "Load topics json"

    def handle(self, *args, **options):
        for filename in glob.glob("answers/*.json"):
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, str):
                    data = json.loads(data)
                valid_choices = [
                    choice[0] for choice in Topic._meta.get_field("topic_type").choices
                ]
                main_topics = data.get("main_topics")
                topics_dict = dict()
                total_percentage = 0
                if isinstance(main_topics, dict):
                    for topic, percentage in main_topics.items():
                        topic = self.camel_to_snake(topic)
                        topic = topic.replace(" ", "_")
                        if topic not in valid_choices:
                            continue
                        elif Topic.objects.filter(
                            topic_type=topic,
                            video=Video.objects.get(url=data.get("url")),
                        ).exists():
                            continue
                        else:
                            if isinstance(percentage, str) and "%" in percentage:
                                percentage = int(percentage.strip("%"))
                            topics_dict[topic] = percentage
                            total_percentage += percentage
                elif isinstance(main_topics, list) and all(
                    isinstance(item, list) and len(item) == 2 for item in main_topics
                ):
                    for topic, percentage in main_topics:
                        if topic not in valid_choices:
                            continue
                        elif Topic.objects.filter(
                            topic_type=topic,
                            video=Video.objects.get(url=data.get("url")),
                        ).exists():
                            continue
                        else:
                            if isinstance(percentage, str) and "%" in percentage:
                                percentage = int(percentage.strip("%"))
                            topics_dict[topic] = percentage
                            total_percentage += percentage
                elif isinstance(main_topics, list) and all(
                    isinstance(item, dict) and len(item) == 1 for item in main_topics
                ):
                    for item in main_topics:
                        for topic, percentage in item.items():
                            topic = self.camel_to_snake(topic)
                            topic = topic.replace(" ", "_")
                            if topic not in valid_choices:
                                continue
                            elif Topic.objects.filter(
                                topic_type=topic,
                                video=Video.objects.get(url=data.get("url")),
                            ).exists():
                                continue
                            else:
                                if isinstance(percentage, str) and "%" in percentage:
                                    percentage = int(percentage.strip("%"))
                                topics_dict[topic] = percentage
                                total_percentage += percentage
                else:
                    print(f"Invalid main topics for {data.get('url')}")

                for topic, percentage in topics_dict.items():
                    if percentage == 0:
                        continue
                    Topic.objects.create(
                        topic_type=topic,
                        percentage=percentage / total_percentage * 100,
                        video=Video.objects.get(url=data.get("url")),
                    )

    def camel_to_snake(self, name):
        name_without_accents = "".join(
            c
            for c in unicodedata.normalize("NFD", name)
            if unicodedata.category(c) != "Mn"
        )
        return "".join(
            [
                "_" + c.lower() if c.isupper() and i != 0 else c.lower()
                for i, c in enumerate(name_without_accents)
            ]
        )
