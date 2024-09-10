# store/serializers.py

from rest_framework import serializers
from .models import Item, ExamCategory, Order



class ExamCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCategory
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    category = ExamCategorySerializer()
    class Meta:
        model = Item
        fields = '__all__'

class ItemPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)
    class Meta:
        model = Order
        fields = '__all__'