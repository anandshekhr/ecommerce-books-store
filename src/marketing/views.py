from django.shortcuts import render, HttpResponse
import pandas as pd
import os
from .models import *
from .serializer import ContactUsSerializer
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
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination
from django_filters import FilterSet
from django.db.models import Q,F
import django_filters
from django.db.models.functions import TruncDate

from django.utils import timezone

import re

def sanitize_mobile_number(mobile_number):
    if not isinstance(mobile_number, str):
        mobile_number = str(mobile_number)

    # Step 1: Remove all white spaces from the input
    sanitized_number = re.sub(r'\s+', '', mobile_number)
    
    # Step 2: Check if the length is greater than 10
    if len(sanitized_number) > 10:
        # Step 3: Remove '0', '+91', or '91' prefix if present
        if sanitized_number.startswith('+91'):
            sanitized_number = sanitized_number[3:]  # Remove the '+91'
        elif sanitized_number.startswith('91'):
            sanitized_number = sanitized_number[2:]  # Remove the '91'
        elif sanitized_number.startswith('0'):
            sanitized_number = sanitized_number[1:]  # Remove the leading '0'
    if sanitized_number.startswith('-'):
        sanitized_number = sanitized_number[1:]
    
    # Step 4: Return the sanitized number (last 10 digits)
    return sanitized_number

from datetime import datetime

def convert_to_standard_date(date_input):
    # Check if the input is a Timestamp, and if so, convert to string
    if isinstance(date_input, pd.Timestamp):
        date_str = date_input.strftime("%d-%b-%y")
    else:
        date_str = date_input  # if already a string

    # Convert the string into a datetime object
    date_obj = datetime.strptime(date_str, "%d-%b-%y")
    
    # Return the date in the standard format YYYY-MM-DD
    return date_obj.strftime("%Y-%m-%d")

# Create your views here.
def read_xls_and_write_to_db(request):
    df = pd.read_excel(os.path.join(os.getcwd(),'marketing/data/teachers_1.xlsx'))
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]

    for index, row in df.iterrows():
        EmailWhatsappTable.objects.get_or_create(
            name = row['name'],
            gender = row['gender'],
            email = row['email_id'],
            mobile = sanitize_mobile_number(row['mobile_no.']),
            city = row['current_location'],
            address= row['address'],
            description = row['area_of_specialization'],
            active=True,
            job_title = row['resume_title'],
            business= row['industry'],
            dob = convert_to_standard_date(row['date_of_birth'])
        )
    return HttpResponse('Success')

class ContactUsApi(generics.ListCreateAPIView):
    queryset = ContactUsFormMarketing.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name','email','phone']
    filterset_fields = ['name','email','phone']
    ordering_fields = ['created_at']