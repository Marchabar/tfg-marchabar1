from django.urls import path
from django.urls.conf import include

from apps.base import views

urlpatterns = [
    path("", views.load_general, name="homepage"),
    path("by-party", views.load_charts, name="party"),
    path(
        "by-politician",
        views.load_politician,
        name="politician",
    ),
    path("falacies/<int:falacy_id>", views.falacy_info, name="falacy_info"),
]
