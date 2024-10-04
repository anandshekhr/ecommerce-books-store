from django.urls import path
from .views import adminUserProfile

urlpatterns = [
    path('profile/',adminUserProfile,name="educator-user-profile")
]
