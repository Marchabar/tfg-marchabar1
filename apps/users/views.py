import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
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
        {
            "user": user,
            "published_number": published_number,
            "videos": videos,
        },
    )


class PasswordChangeFormView(View):
    def post(self, request):
        user = request.user
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not user.check_password(old_password):
            return JsonResponse(
                {"success": False, "message": "La contraseña actual es incorrecta."}
            )
        else:
            if new_password != confirm_password:
                return JsonResponse(
                    {"success": False, "message": "Las contraseñas no coinciden."}
                )
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return JsonResponse({"success": True})


class AvatarChangeView(View):
    def post(self, request):
        user = request.user
        avatar = request.FILES.get("avatar")
        if not avatar:
            return JsonResponse({"success": False, "message": "No hay ninguna imagen"})
        ext = os.path.splitext(avatar.name)[1]  # Get the file extension
        valid_extensions = [".jpg", ".jpeg", ".png"]
        if ext.lower() not in valid_extensions:
            return JsonResponse({"success": False, "message": "Invalid file type."})
        user.avatar = avatar
        user.save()
        return JsonResponse({"success": True})


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
