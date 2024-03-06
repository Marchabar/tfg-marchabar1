from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.urls.conf import include

from apps.users import views

urlpatterns = [
    path("profile", views.index, name="my-profile"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("signup", views.SignUpView.as_view(), name="signup"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
