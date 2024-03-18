from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    uploaded_videos = models.IntegerField(default=0)

    def __str__(self):
        return self.username
