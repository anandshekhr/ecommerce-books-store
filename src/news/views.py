from django.shortcuts import render
import requests
from .models import NewsTheHindu
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from main.core.pagination import StandardResultsSetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from .serializers import *

class NewsHeadlines(generics.ListAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = NewsHeadLinesSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Add default sorting by 'created_at' in descending order
        return NewsTheHindu.objects.all().order_by('-created_at')

class NewsDetails(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    queryset = NewsTheHindu.objects.all()
    serializer_class = NewsDetailsSerializer
    pagination_class = PageNumberPagination