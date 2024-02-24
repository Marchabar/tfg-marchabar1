import glob
import json

from django.core.management.base import BaseCommand
from unidecode import unidecode

from apps.videos.models import Video

from ...models import Topic


class Command(BaseCommand):
    help = "Load language json"

    def handle(self, *args, **options):
        for filename in glob.glob("answers/*.json"):
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                valid_choices = [
                    choice[0] for choice in Topic._meta.get_field("topic_type").choices
                ]
                main_topics = data.get("main_topics")
                topics_dict = {}
                total_percentage = 0
                if isinstance(main_topics, dict):
                    for topic, percentage in main_topics.items():
                        if topic not in valid_choices:
                            break
                        elif Topic.objects.filter(
                            topic_type=topic,
                            video=Video.objects.get(url=data.get("url")),
                        ).exists():
                            break
                        else:
                            topics_dict[topic] = percentage
                            total_percentage += percentage
                    for topic, percentage in topics_dict.items():
                        Topic.objects.create(
                            topic_type=topic,
                            percentage=percentage / total_percentage * 10,
                            video=Video.objects.get(url=data.get("url")),
                        )
                elif isinstance(main_topics, list) and all(
                    isinstance(item, list) and len(item) == 2 for item in main_topics
                ):
                    for topic, percentage in main_topics:
                        if topic not in valid_choices:
                            break
                        elif Topic.objects.filter(
                            topic_type=topic,
                            video=Video.objects.get(url=data.get("url")),
                        ).exists():
                            break
                        else:
                            topics_dict[topic] = percentage
                            total_percentage += percentage
                    for topic, percentage in topics_dict.items():
                        Topic.objects.create(
                            topic_type=topic,
                            percentage=percentage / total_percentage * 10,
                            video=Video.objects.get(url=data.get("url")),
                        )
