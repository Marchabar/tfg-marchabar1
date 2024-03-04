from django.urls import path
from django.urls.conf import include

from apps.users import views

urlpatterns = [
    path("profile", views.index, name="my-profile"),
]
