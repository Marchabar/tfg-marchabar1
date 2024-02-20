from django.db import models

# Create your models here.

class Sentiment(models.Model):
    SENTIMENT_CHOICES = [
        ("enojo", "Enojo"),
        ("frustracion", "Frustración"),
        ("pasion", "Pasión"),
        ("entusiasmo", "Entusiasmo"),
        ("preocupacion", "Preocupación"),
        ("confianza", "Confianza"),
        ("desesperacion", "Desesperación"),
        ("optimismo", "Optimismo"),
        ("satisfaccion", "Satisfacción"),
        ("escepticismo", "Escepticismo"),
        ("desden", "Desdén"),
        ("empatia", "Empatía")
    ]
    sentiment_type = models.TextField(choices=SENTIMENT_CHOICES)
    video = models.ForeignKey("videos.Video", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sentiment_type} - {self.video.title}"
