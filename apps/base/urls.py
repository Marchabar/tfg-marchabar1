from django.urls import path
from django.urls.conf import include

from apps.base import views

urlpatterns = [
    path("", views.load_charts, name="homepage"),
]