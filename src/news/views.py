from django.shortcuts import render
import requests
from .models import NewsTheHindu
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import *

class NewsHeadlines(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = NewsTheHindu.objects.all().order_by('updated_at')
    serializer_class = NewsHeadLinesSerializer
    pagination_class = PageNumberPagination

class NewsDetails(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = NewsTheHindu.objects.all()
    serializer_class = NewsDetailsSerializer
    pagination_class = PageNumberPagination