from django.contrib.auth import authenticate, login, logout
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
            # Redirect to a success page or dashboard
            return redirect(
                "/"
            )  # Replace 'dashboard' with the URL name of your dashboard page
        else:
            # Authentication failed, render login form with error message
            return redirect("/")


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("/")
