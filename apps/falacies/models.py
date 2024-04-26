from django.db import models

# Create your models here.


class Falacy(models.Model):
    title = models.CharField(max_length=255)
    politician = models.TextField()
    PARTIES_CHOICES = [
        ("PP", "Partido Popular"),
        ("PSOE", "Partido Socialista Obrero Español"),
        ("SUMAR", "Sumar"),
        ("VOX", "Vox"),
    ]
    political_party = models.TextField(choices=PARTIES_CHOICES)
    argument = models.TextField()
    image = models.ImageField(upload_to="falacies/", null=True, blank=True)

    def __str__(self):
        return self.title
