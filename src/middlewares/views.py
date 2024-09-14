import os
from rest_framework import generics, status, authentication, permissions,filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, get_user_model,login
from django.http import JsonResponse
from django.db.models import Max, Min, Count, Avg
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination
from django_filters import FilterSet
from django.db.models import Q
import django_filters

from .serializer import *
from .models import *


class DataLogAPI(generics.ListAPIView):
    serializer_class = RequestDataLogSerializer
    pagination_class = PageNumberPagination
    authentication_classes = (SessionAuthentication,TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = RequestDataLog.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ('method','path','body','user_agent','client_ip','country','mobile','is_new_user','timestamp')
    search_fields = ('method','path','body','user_agent','client_ip','country','mobile','is_new_user','timestamp')
    ordering_fields = ('method','path','user_agent','client_ip','country','mobile','is_new_user','timestamp')

