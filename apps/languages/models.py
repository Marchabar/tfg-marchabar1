from django.db import models


# Create your models here.

class Language(models.Model):
    LANGUAGE_CHOICES = [
        ("formal", "Lenguaje formal"),
        ("tecnico", "Lenguaje técnico"),
        ("emocional", "Lenguaje emocional"),
        ("persuasivo", "Lenguaje persuasivo"),
        ("retorico", "Lenguaje retórico"),
        ("bipartidista", "Lenguaje bipartidista"),
        ("partidista", "Lenguaje partidista"),
        ("populista", "Lenguaje populista"),
        ("consenso", "Lenguaje de consenso"),
        ("confrontacion", "Lenguaje de confrontación"),
        ("compromiso", "Lenguaje de compromiso"),
        ("promesas", "Lenguaje de promesas"),
        ("critica", "Lenguaje de crítica"),
        ("estadisticas", "Lenguaje de estadísticas"),
        ("datos", "Lenguaje de datos"),
        ("debate", "Lenguaje de debate"),
        ("discurso_publico", "Lenguaje de discurso público"),
        ("campana", "Lenguaje de campaña"),
        ("legislacion", "Lenguaje de legislación"),
        ("negociacion", "Lenguaje de negociación"),
        ("patriótico", "Lenguaje patriótico"),
    ]
    language_type = models.TextField(choices=LANGUAGE_CHOICES)
    video = models.ForeignKey("videos.Video", on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.language_type} - {self.video.title}"