from rest_framework import serializers
from .models import *

class RequestDataLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestDataLog
        fields = '__all__'

