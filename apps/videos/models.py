from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    thumbnail = models.ImageField(upload_to="thumbnails/")
    length = models.FloatField()
    date = models.DateField(auto_now_add=True)
    politician_name = models.CharField(max_length=100) 
    PARTIES_CHOICES = [
        ('PP', 'Partido Popular'),
        ('PSOE', 'Partido Socialista Obrero Español'),
        ('SUMAR', 'Sumar'),
        ('VOX', 'Vox'),
    ]
    political_party = models.TextField(choices=PARTIES_CHOICES)

    def __str__(self):
        return f"{self.title} - {self.date}"