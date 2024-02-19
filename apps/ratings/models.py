from django.db import models

# Create your models here.


class Rating(models.Model):
    rating = models.IntegerField()
    description = models.TextField()
    creator = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    video = models.ForeignKey("videos.Video", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.rating} - {self.description}"