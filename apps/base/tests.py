from django.test import Client, TestCase
from django.urls import reverse

from apps.base.views import load_charts


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
