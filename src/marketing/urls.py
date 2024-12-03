from django.urls import path
from .views import *
urlpatterns = [
    path('load', read_xls_and_write_to_db),
    path('add/contact-us',ContactUsApi.as_view()),
]
