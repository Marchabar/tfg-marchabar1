from datetime import date

from django.test import Client, TestCase
from django.urls import reverse

from apps.languages.models import Language
from apps.sentiments.models import Sentiment
from apps.topics.models import Topic
from apps.users.models import CustomUser
from apps.videos.models import Video
from apps.words.models import Word


class VideoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_superuser(
            username="testuser", password="12345"
        )
        self.video = Video.objects.create(
            title="Video 1",
            url="http://example.com/video1",
            length="00:10:00",
            summary="This is a summary for video 1",
            date="2022-01-01",
            politician_name="Politician 1",
            political_party="PP",
            published=True,
            user=self.user,
        )
        self.topic = Topic.objects.create(
            video=self.video, topic_type="test", percentage=50
        )
        self.sentiment = Sentiment.objects.create(
            video=self.video, sentiment_type="positive"
        )
        self.language = Language.objects.create(
            video=self.video, language_type="formal"
        )
        self.word = Word.objects.create(video=self.video, word="test")

    def test_publish_video(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(reverse("publish_video", args=[self.video.id]))
        self.assertEqual(response.status_code, 200)
        self.video.refresh_from_db()
        self.assertTrue(self.video.published)

    def test_all_videos(self):
        response = self.client.get(reverse("all-videos"))
        self.assertEqual(
            response.status_code, 302
        )  # Expecting a redirect because the user is not authenticated
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("all-videos"))
        self.assertEqual(response.status_code, 200)

    def test_get_video_information(self):
        response = self.client.get(reverse("video", args=[self.video.id]))
        self.assertEqual(response.status_code, 200)
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("video", args=[self.video.id]))
        self.assertEqual(response.status_code, 200)

    def test_get_videos_by_topic(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("topic", args=["economia"]))
        self.assertEqual(response.status_code, 200)

    def test_analyze_video_user(self):
        Video.objects.create(
            title="Video 10",
            url="https://youtu.be/test_video",
            length="00:10:00",
            summary="This is a summary for video 1",
            date=date.today(),
            politician_name="Politician 1",
            political_party="PP",
            published=True,
            user=self.user,
        )

        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("analysis"), {"video-url": "https://youtu.be/test_video"}
        )

        self.assertEqual(response.status_code, 200)


class VideosUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username="user2", password="12345")
        self.video = Video.objects.create(
            title="Video 1",
            url="http://example.com/video1",
            length="00:10:00",
            summary="This is a summary for video 1",
            date=date.today(),
            politician_name="Politician 1",
            political_party="PP",
            published=True,
            user=self.user,
        )

    def test_get_videos_by_user(self):
        self.client.login(username="user2", password="12345")
        response = self.client.get(reverse("my-videos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.video.title)
