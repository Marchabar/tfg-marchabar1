import json
import os
import tempfile
from datetime import datetime

from django.core.management import call_command
from django.test import TestCase

from apps.topics.models import Topic
from apps.videos.models import Video

# Create your tests here.


class LoadTopicsJsonTest(TestCase):
    def setUp(self):
        self.data = {
            "politician_name": "Pablo Bustinduy",
            "political_party": "SUMAR",
            "url": "https://youtu.be/tRtioYJYOFc?si=Iu7OswNT-RDt-a8j",
            "date": "15/01/2024",
            "summary": "En este emotivo mitin político, el orador destaca los desafíos globales que enfrenta el mundo, desde conflictos en Ucrania hasta la crisis en Argentina y el resurgimiento de la extrema derecha en Europa. Se expresa un firme apoyo a la demanda de Sudáfrica contra Israel por el genocidio palestino y se insta a España a unirse a esta causa. El discurso se centra en la urgente necesidad de promover el bienestar, la certeza democrática y la justicia social en España, destacando medidas concretas para lograrlo. Se subraya la importancia de mantener la visión de una sociedad mejor como una 'idealidad permanente' y se promete un compromiso incansable para alcanzar ese objetivo. El discurso concluye con un llamado a la acción y un mensaje de esperanza en la construcción de un futuro democrático y justo.",
            "length": "07:04",
            "main_topics": {
                "Medio ambiente": 5,
                "Derechos civiles": 10,
                "Inmigración": 5,
                "Seguridad nacional": 5,
                "Política exterior": 10,
                "Criminalidad": 5,
                "Paz y conflicto": 15,
                "Defensa": 5,
                "Legislación": 10,
                "Justicia": 10,
                "Derechos de las minorías": 10,
            },
            "sentiment": ["Escepticismo", "Optimismo", "Entusiasmo"],
            "lenguaje": [
                "Lenguaje formal",
                "Lenguaje de discurso público",
                "Lenguaje de legislación",
                "Lenguaje de compromiso",
            ],
            "used_words": [
                "democrática",
                "sociedad",
                "derechos",
                "España",
                "justicia",
                "política",
                "vida",
                "mundo",
                "pueblo",
                "compromiso",
            ],
        }

        self.temp_file = tempfile.NamedTemporaryFile(
            delete=False, mode="w+t", dir="answers"
        )
        json.dump(self.data, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        # Delete the temporary file
        os.remove(self.temp_file.name)

    def test_handle(self):
        call_command("load_video_json")
        call_command("load_topics_json")

        # Check that a Video object was created
        video = Video.objects.get(url=self.data["url"])
        self.assertIsNotNone(video)
        self.assertEqual(video.politician_name, self.data["politician_name"])
        self.assertEqual(video.political_party, self.data["political_party"])
        # Convert the date string to a datetime.date object
        date = datetime.strptime(self.data["date"], "%d/%m/%Y").date()
        self.assertEqual(video.date, date)

        self.assertEqual(video.summary, self.data["summary"])
        self.assertEqual(video.length, self.data["length"])

        topics = Topic.objects.filter(video=video)

        self.assertEqual(len(topics), len(self.data["main_topics"]))
