from rest_framework import serializers
from .models import *

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUsFormMarketing
        fields  = '__all__'
        