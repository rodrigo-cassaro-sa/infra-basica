import os
from django.http import JsonResponse


def health(request):
    return JsonResponse({
        "status": "ok",
        "service": "django",
        "settings": os.getenv("DJANGO_SETTINGS_MODULE", "unknown"),
    })
