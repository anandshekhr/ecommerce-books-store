from rest_framework import serializers
from .models import *

class RequestDataLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestDataLog
        fields = '__all__'


class ErrorLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = ErrorLog
        fields = '__all__'
        