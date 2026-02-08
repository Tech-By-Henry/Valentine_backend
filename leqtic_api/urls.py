# leqtic_api/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # we expose endpoints at root: /valentine/ and /valentine/<uuid>/
    path("", include("valentines.urls")),
]
