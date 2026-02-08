# valentines/urls.py
from django.urls import path
from .views import CreateValentineAPIView, ValentineDetailAPIView

urlpatterns = [
    path("valentine/", CreateValentineAPIView.as_view(), name="create-valentine"),
    path("valentine/<uuid:id>/", ValentineDetailAPIView.as_view(), name="valentine-detail"),
]
