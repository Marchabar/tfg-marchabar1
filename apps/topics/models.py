from django.db import models

# Create your models here.

class Topic(models.Model):
    TOPIC_CHOICES = [
        ("economia", "Economía"),
        ("salud", "Salud"),
        ("educacion", "Educación"),
        ("medio_ambiente", "Medio ambiente"),
        ("derechos_civiles", "Derechos civiles"),
        ("inmigracion", "Inmigración"),
        ("seguridad_nacional", "Seguridad nacional"),
        ("politica_exterior", "Política exterior"),
        ("empleo", "Empleo"),
        ("criminalidad", "Criminalidad"),
        ("impuestos", "Impuestos"),
        ("bienestar_social", "Bienestar social"),
        ("tecnologia", "Tecnología"),
        ("energia", "Energía"),
        ("vivienda", "Vivienda"),
        ("corrupcion", "Corrupción"),
        ("libertad_de_prensa", "Libertad de prensa"),
        ("igualdad_de_genero", "Igualdad de género"),
        ("diversidad_y_discriminacion", "Diversidad y discriminación"),
        ("pobreza", "Pobreza"),
        ("infraestructura", "Infraestructura"),
        ("religion", "Religión"),
        ("derechos_de_las_minorias", "Derechos de las minorías"),
        ("paz_y_conflicto", "Paz y conflicto"),
        ("defensa", "Defensa"),
        ("legislacion", "Legislación"),
        ("presupuesto", "Presupuesto"),
        ("justicia", "Justicia")
    ]
    topic_type = models.TextField(choices=TOPIC_CHOICES)
    video = models.ForeignKey("videos.Video", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.topic_type} - {self.video.title}"