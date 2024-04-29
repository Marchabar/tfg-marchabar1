import json
from datetime import date

from django.conf import settings
from django.core.files import File
from django.db.models.query import QuerySet
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from apps.base.views import load_charts
from apps.languages.models import Language
from apps.sentiments.models import Sentiment
from apps.topics.models import Topic
from apps.users.models import CustomUser
from apps.videos.models import Video
from apps.words.models import Word


class LoadGeneralTestCase(TestCase):
    def setUp(self):
        self.video1 = Video.objects.create(
            title="Video 1",
            url="http://example.com/video1",
            length="00:10:00",
            summary="This is a summary for video 1",
            date=date.today(),
            politician_name="Politician 1",
            political_party="PP",
            published=True,
        )
        self.video2 = Video.objects.create(
            title="Video 2",
            url="http://example.com/video2",
            length="00:10:00",
            summary="This is a summary for video 2",
            date=date.today(),
            politician_name="Politician 2",
            political_party="PSOE",
            published=True,
        )
        self.topic1 = Topic.objects.create(
            video=self.video1, topic_type="Topic1", percentage=0.5
        )
        self.topic2 = Topic.objects.create(
            video=self.video1, topic_type="Topic2", percentage=0.3
        )
        self.topic3 = Topic.objects.create(
            video=self.video2, topic_type="Topic1", percentage=0.2
        )
        self.sentiment1 = Sentiment.objects.create(
            video=self.video1, sentiment_type="Sentiment1"
        )
        self.sentiment2 = Sentiment.objects.create(
            video=self.video1, sentiment_type="Sentiment2"
        )
        self.sentiment3 = Sentiment.objects.create(
            video=self.video2, sentiment_type="Sentiment1"
        )
        self.language1 = Language.objects.create(
            video=self.video1, language_type="Language1"
        )
        self.language2 = Language.objects.create(
            video=self.video1, language_type="Language2"
        )
        self.language3 = Language.objects.create(
            video=self.video2, language_type="Language1"
        )
        self.word1 = Word.objects.create(video=self.video1, word="Word1")
        self.word2 = Word.objects.create(video=self.video1, word="Word2")
        self.word3 = Word.objects.create(video=self.video2, word="Word3")

    def test_load_general(self):
        url = reverse("homepage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "general.html")
        dict_general_json = response.context["dict_general"]
        dict_general = json.loads(dict_general_json)

        # Check if the dict_general has the expected structure and values
        self.assertEqual(len(dict_general), 2)
        self.assertIn("PP", dict_general)
        self.assertIn("PSOE", dict_general)

        party1_values = dict_general["PP"]
        self.assertIn("topics", party1_values)
        self.assertIn("sentiments", party1_values)
        self.assertIn("languages", party1_values)

        topics = party1_values["topics"]
        self.assertIn("Topic1", topics)
        self.assertIn("Topic2", topics)
        self.assertAlmostEqual(topics["Topic1"], 62.5)
        self.assertAlmostEqual(topics["Topic2"], 37.5)

        sentiments = party1_values["sentiments"]
        self.assertIn("Sentiment1", sentiments)
        self.assertIn("Sentiment2", sentiments)
        self.assertEqual(sentiments["Sentiment1"], 1)
        self.assertEqual(sentiments["Sentiment2"], 1)

        languages = party1_values["languages"]
        self.assertIn("Language1", languages)
        self.assertIn("Language2", languages)
        self.assertEqual(languages["Language1"], 1)
        self.assertEqual(languages["Language2"], 1)

        party2_values = dict_general["PSOE"]
        self.assertIn("topics", party2_values)
        self.assertIn("sentiments", party2_values)
        self.assertIn("languages", party2_values)

        topics = party2_values["topics"]
        self.assertIn("Topic1", topics)
        self.assertAlmostEqual(topics["Topic1"], 100.0)

        sentiments = party2_values["sentiments"]
        self.assertIn("Sentiment1", sentiments)
        self.assertEqual(sentiments["Sentiment1"], 1)

        languages = party2_values["languages"]
        self.assertIn("Language1", languages)
        self.assertEqual(languages["Language1"], 1)


class LoadPoliticianTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create(username="testuser", password="12345")
        self.video1 = Video.objects.create(
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
        self.sentiment1 = Sentiment.objects.create(
            video=self.video1, sentiment_type="Positive"
        )
        self.language1 = Language.objects.create(
            video=self.video1, language_type="English"
        )
        self.topic1 = Topic.objects.create(
            video=self.video1, topic_type="Politics", percentage=80
        )

    def test_load_politician(self):
        url = reverse("politician")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "politician.html")

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected context variables
        self.assertIn("dict_politicians", response.context)
        self.assertIn("dict_sentiments", response.context)
        self.assertIn("dict_languages", response.context)
        self.assertIn("dict_topics", response.context)
        self.assertIn("politicians", response.context)
        self.assertIn("videos", response.context)

        # Assert that the response context variables have the expected types
        self.assertIsInstance(response.context["dict_politicians"], dict)
        self.assertIsInstance(response.context["dict_sentiments"], dict)
        self.assertIsInstance(response.context["dict_languages"], dict)
        self.assertIsInstance(response.context["dict_topics"], dict)
        self.assertIsInstance(response.context["politicians"], QuerySet)
        self.assertIsInstance(response.context["videos"], QuerySet)


class LoadChartsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create(username="testuser", password="12345")
        self.video1 = Video.objects.create(
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
        self.sentiment1 = Sentiment.objects.create(
            video=self.video1, sentiment_type="Positive"
        )
        self.language1 = Language.objects.create(
            video=self.video1, language_type="Critica"
        )
        self.topic1 = Topic.objects.create(
            video=self.video1, topic_type="Politics", percentage=80
        )
        self.word1 = Word.objects.create(video=self.video1, word="test")

    def test_load_charts(self):
        url = reverse("party")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "home.html")

        self.assertEqual(response.status_code, 200)
        self.assertIn("dict_topics", response.context)
        self.assertIn("dict_sentiments", response.context)
        self.assertIn("dict_languages", response.context)
        self.assertIn("videos", response.context)
        self.assertIn("dict_words", response.context)
