import glob
import json
import re
from datetime import datetime

import environ
import requests
from django.core.management.base import BaseCommand

from ...models import Video

env = environ.Env()


class Command(BaseCommand):
    help = "Load video json"

    def handle(self, *args, **options):
        for filename in glob.glob("answers/*.json"):
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                valid_choices = [
                    choice[0]
                    for choice in Video._meta.get_field("political_party").choices
                ]

                video_url = data.get("url")

                if video_url:
                    video_id = self.extract_video_id(video_url)
                    if video_id:
                        video_details = self.get_video_details(video_id)
                        if video_details:
                            title = video_details.get("title")
                            thumbnail = video_details.get("thumbnail")
                            if data.get("political_party") not in valid_choices:
                                break
                            else:
                                date = datetime.strptime(data.get("date"), "%d/%m/%Y")

                                if title not in [
                                    video.title for video in Video.objects.all()
                                ]:
                                    Video.objects.create(
                                        title=title,
                                        url=video_url,
                                        thumbnail=thumbnail,
                                        length=data.get("length"),
                                        summary=data.get("summary"),
                                        date=date,
                                        politician_name=data.get("politician_name"),
                                        political_party=data.get("political_party"),
                                    )

    def extract_video_id(self, video_url):
        match = re.search(
            r'(?:youtu\.be\/|youtube\.com\/(?:.*\/v\/|.*[?&]v=|.*[?&]vi=))([^"&?\/\s]{11})',
            video_url,
        )
        if match:
            return match.group(1)
        return None

    def get_video_details(self, video_id):
        youtube_api_key = env("YOUTUBE_API_KEY")
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={youtube_api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "items" in data and data["items"]:
                snippet = data["items"][0]["snippet"]
                title = snippet.get("title")
                thumbnail = snippet.get("thumbnails").get("default").get("url")
                return {"title": title, "thumbnail": thumbnail}
        return None
