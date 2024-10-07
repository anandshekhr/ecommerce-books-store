from rest_framework import serializers
from .models import NewsTheHindu

class NewsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTheHindu
        fields = '__all__'

class NewsHeadLinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTheHindu
        fields = ['id','headline','sub_title','author','publish_time','created_at','updated_at']