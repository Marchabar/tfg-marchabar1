from django.db import models

# Create your models here.

class Word(models.Model):
    word = models.TextField()
    video = models.ForeignKey("videos.Video", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.word} - {self.video.title}"

    