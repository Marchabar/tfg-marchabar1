import json
from datetime import date

from django.conf import settings
from django.core.files import File
from django.test import Client, TestCase
from django.urls import reverse

from apps.base.views import load_charts
from apps.languages.models import Language
from apps.sentiments.models import Sentiment
from apps.topics.models import Topic
from apps.videos.models import Video


class LoadGeneralTestCase(TestCase):
    def setUp(self):
        self.video1 = Video.objects.create(
            title="Video 1",
            url="http://example.com/video1",
            length="00:10:00",
            summary="This is a summary for video 1",
            date=date.today(),
            politician_name="Politician 1",
            political_party="Party1",
            published=True,
        )
        self.video2 = Video.objects.create(
            title="Video 2",
            url="http://example.com/video2",
            length="00:10:00",
            summary="This is a summary for video 2",
            date=date.today(),
            politician_name="Politician 2",
            political_party="Party2",
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

    def test_load_general(self):
        url = reverse("homepage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "general.html")
        dict_general_json = response.context["dict_general"]
        dict_general = json.loads(dict_general_json)

        # Check if the dict_general has the expected structure and values
        self.assertEqual(len(dict_general), 2)
        self.assertIn("Party1", dict_general)
        self.assertIn("Party2", dict_general)

        party1_values = dict_general["Party1"]
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

        party2_values = dict_general["Party2"]
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


class LoadChartsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_load_charts(self):
        response = self.client.get("/by-party")

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the context data contains the expected keys
        self.assertIn("dict_topics", response.context)
        self.assertIn("dict_sentiments", response.context)
        self.assertIn("dict_languages", response.context)
        self.assertIn("videos", response.context)
