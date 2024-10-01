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
    # authentication_classes = (SessionAuthentication,TokenAuthentication)
    queryset = RequestDataLog.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ('method','path','body','user_agent','client_ip','country','mobile','is_new_user','timestamp')
    search_fields = ('method','path','body','user_agent','client_ip','country','mobile','is_new_user','timestamp')
    ordering_fields = ('method','path','user_agent','client_ip','country','mobile','is_new_user','timestamp')

    def get(self, request, *args, **kwargs):
        if 'summary' in request.query_params:
            summary_data = {}

            # Get today's date and calculate last 7 days
            today = timezone.now().date()
            last_seven_days = today - timezone.timedelta(days=7)

            # Daily path requests for the last 7 days
            daily_paths = (
                RequestDataLog.objects
                .filter(timestamp__date__gte=last_seven_days)
                .exclude(path__contains='admin')
                .exclude(path__contains='sitemap')
                .exclude(path__contains='favicon')
                .exclude(path__contains='platform')
                .exclude(path__contains='accounts')
                .values('timestamp', 'path')
            )

            # Organizing data for the line graph
            path_growth_data = defaultdict(lambda: defaultdict(int))
            for entry in daily_paths:
                timestamp = entry['timestamp']
                date_str = timestamp.date().isoformat()  # Convert date to string
                path = entry['path']
                path_growth_data[path][date_str] += 1

            # Calculate total requests per path and get top 5 paths
            total_path_counts = {
                path: sum(counts.values()) for path, counts in path_growth_data.items()
            }
            top_paths = sorted(total_path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            top_path_growth_data = {path: path_growth_data[path] for path, _ in top_paths}

            summary_data['path_growth'] = top_path_growth_data

            # Count new users based on distinct IPs for the last 7 days, grouped by day
            distinct_ips = RequestDataLog.objects.filter(
                timestamp__date__gte=last_seven_days,  # Filter for last 7 days
                is_new_user=True                       # Filter for new users
            ).annotate(date=TruncDate('timestamp'))    # Truncate timestamp to the date level
            distinct_ip_count_per_day = distinct_ips.values('date').annotate(
                distinct_ip_count=Count('client_ip', distinct=True)  # Count distinct client IPs per day
            ).order_by('date')  # Ensure the data is ordered by the date

            new_users_data = {'mobile': {}, 'web': {}}

            # Fetch counts for mobile and web users separately
            for entry in distinct_ip_count_per_day:
                date_str = entry['date'].isoformat()  # Convert date to string in 'YYYY-MM-DD' format
                distinct_ip_count = entry['distinct_ip_count']

                # You can further refine mobile vs web logic here if needed
                # For now, adding the distinct IP count to 'web' and 'mobile' assuming the distinction is handled elsewhere
                new_users_data['web'].setdefault(date_str, 0)
                new_users_data['web'][date_str] += distinct_ip_count

            # Add the data to the response
            summary_data['new_users'] = new_users_data

            return Response(summary_data, status=status.HTTP_200_OK)
        queryset = self.filter_queryset(self.get_queryset())

        # Use the paginator defined in the class to paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # If pagination is not needed or not enabled, return a normal response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

def getGraphOverview(request):
    return render(request,'graph.html')
