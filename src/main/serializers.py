# store/serializers.py

from rest_framework import serializers
from .models import Item, ExamCategory, Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class ExamCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCategory
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    category = ExamCategorySerializer()
    class Meta:
        model = Item
        fields = '__all__'