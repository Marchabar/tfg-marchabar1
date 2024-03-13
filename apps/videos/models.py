from django.db import models

from apps.users.models import CustomUser

# Create your models here.


class Video(models.Model):
    title = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    thumbnail = models.ImageField(upload_to="thumbnails/")
    length = models.TextField()
    summary = models.TextField()
    date = models.DateField()
    politician_name = models.CharField(max_length=100)
    PARTIES_CHOICES = [
        ("PP", "Partido Popular"),
        ("PSOE", "Partido Socialista Obrero Español"),
        ("SUMAR", "Sumar"),
        ("VOX", "Vox"),
    ]
    political_party = models.TextField(choices=PARTIES_CHOICES)
    published = models.BooleanField(default=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.title} - {self.date}"
