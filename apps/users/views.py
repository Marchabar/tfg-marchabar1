from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

# Create your views here.


def index(request):
    return render(request, "profile.html")


class LoginView(View):
    def get(self, request):
        # Render the login form
        return render(request, "login.html")

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
                {"success": False, "message": "Invalid username or password."}
            )


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("/")
