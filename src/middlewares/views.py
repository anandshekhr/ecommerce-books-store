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
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination
from django_filters import FilterSet
from django.db.models import Q,F
import django_filters
from django.db.models.functions import TruncDate

from django.utils import timezone
from .serializer import *
from .models import *
import datetime
from collections import defaultdict


class DataLogAPI(generics.ListAPIView):
    serializer_class = RequestDataLogSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AllowAny,)
    queryset = RequestDataLog.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('method','path','body','user_agent','client_ip','country','mobile','is_new_user','timestamp')
    search_fields = ('method','path','body','user_agent','client_ip','country','mobile','is_new_user','timestamp')
    ordering_fields = ('method','path','user_agent','client_ip','country','mobile','is_new_user','timestamp')

    def get(self, request, *args, **kwargs):
        # Handle Grafana timestamp filters
        from_param = request.query_params.get('from')
        to_param = request.query_params.get('to')

        queryset = self.get_queryset()

        # Exclude bots based on common user-agent patterns
        bot_keywords = [
            'bot', 'crawl', 'spider', 'curl', 'python', 'postman', 
            'okhttp', 'fetch', 'scrapy', 'headless', 'google', 'bing', 
            'yahoo', 'facebookexternalhit', 'whatsapp', 'telegram'
        ]
        for keyword in bot_keywords:
            queryset = queryset.exclude(user_agent__icontains=keyword)

        if from_param and to_param:
            try:
                # Grafana often sends ISO 8601 timestamps
                from_time = timezone.datetime.fromisoformat(from_param.replace('Z', '+00:00'))
                to_time = timezone.datetime.fromisoformat(to_param.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__gte=from_time, timestamp__lte=to_time)
            except ValueError:
                pass  # fallback to default queryset if parsing fails

        # Check if summary is requested
        if 'summary' in request.query_params:
            summary_data = {}

            daily_paths = (
                queryset
                .exclude(path__contains='admin')
                .exclude(path__contains='sitemap')
                .exclude(path__contains='favicon')
                .exclude(path__contains='platform')
                .exclude(path__contains='accounts')
                .values('timestamp', 'path')
            )

            # Organize data for line graph
            path_growth_data = defaultdict(lambda: defaultdict(int))
            for entry in daily_paths:
                timestamp = entry['timestamp']
                date_str = timestamp.date().isoformat()
                path = entry['path']
                path_growth_data[path][date_str] += 1

            # Top 5 paths
            total_path_counts = {path: sum(counts.values()) for path, counts in path_growth_data.items()}
            top_paths = sorted(total_path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            top_path_growth_data = {path: path_growth_data[path] for path, _ in top_paths}
            summary_data['path_growth'] = top_path_growth_data

            # Count new users
            distinct_ips = queryset.filter(is_new_user=True).annotate(date=TruncDate('timestamp'))
            distinct_ip_count_per_day = distinct_ips.values('date').annotate(distinct_ip_count=Count('client_ip', distinct=True)).order_by('date')

            new_users_data = {'mobile': {}, 'web': {}}
            for entry in distinct_ip_count_per_day:
                date_str = entry['date'].isoformat()
                distinct_ip_count = entry['distinct_ip_count']
                # Add logic to separate mobile vs web if needed
                new_users_data['web'].setdefault(date_str, 0)
                new_users_data['web'][date_str] += distinct_ip_count

            summary_data['new_users'] = new_users_data
            return Response(summary_data, status=status.HTTP_200_OK)

        # Apply filters, pagination, and return
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def getGraphOverview(request):
    return render(request,'graph.html')

class ErrorLogApi(generics.ListCreateAPIView):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user_token','timestamp','error_message','error_details','api_name']
    filterset_fields = ['user_token','timestamp','error_message','error_details','api_name']
    ordering_fields = ['timestamp']

