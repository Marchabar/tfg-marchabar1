from django.urls import path
from django.urls.conf import include

from apps.videos import views

urlpatterns = [
    path("analysis", views.index, name="analysis"),
]
