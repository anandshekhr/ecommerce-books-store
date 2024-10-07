from django.urls import path
from .views import *
urlpatterns = [
    path('headlines',NewsHeadlines.as_view()),
    path('details/<int:pk>',NewsDetails.as_view())
]
