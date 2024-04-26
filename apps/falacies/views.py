from django.shortcuts import render

# Create your views here.


def falacy_info(request, falacy_id):
    falacy = Falacy.objects.get(id=falacy_id)
    return render(request, "falacy-info.html", {"falacy": falacy})
