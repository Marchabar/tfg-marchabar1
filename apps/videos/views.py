from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

# Create your views here.


def analizar_video_usuario(request):
    if not request.user.is_authenticated:
        return redirect("/?login_required=true")
    return render(request, "analysis.html")
