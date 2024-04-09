from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from apps.users.models import CustomUser
from apps.videos.models import Video

# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")
    user = request.user
    videos = Video.objects.filter(user=user)
    user.uploaded_videos = len(videos)
    published = Video.objects.filter(user=user, published=True)
    published_number = len(published)
    return render(
        request,
        "profile.html",
        {"user": user, "published_number": published_number, "videos": videos},
    )


class LoginView(View):

    def post(self, request):
        # Get username and password from the POST data
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # User is authenticated, log in the user
            login(request, user)
            return JsonResponse(
                {"success": True}
            )  # Replace 'dashboard' with the URL name of your dashboard page
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Nombre de usuario o contraseña son inválidos.",
                }
            )


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("/")


class SignUpView(View):

    def post(self, request):
        # Get the POST data
        username = request.POST.get("username")
        # avatar is the attribute for the profile picture of the user
        avatar = request.FILES.get("avatar")
        password = request.POST.get("password")

        # Check if the username already exists
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse(
                {"success": False, "message": "El nombre de usuario ya existe."}
            )

        # Create the user
        user = CustomUser.objects.create_user(
            username=username, password=password, avatar=avatar
        )

        if user is not None:
            # Log in the user
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "No se pudo crear el usuario.",
                }
            )
