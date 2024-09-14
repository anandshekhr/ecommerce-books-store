from django.urls import path
from .views import *



urlpatterns = [
    path("log/overview/",DataLogAPI.as_view(),name="overview"),
]