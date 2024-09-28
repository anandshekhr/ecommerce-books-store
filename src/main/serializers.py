# store/serializers.py

from rest_framework import serializers
from .models import Item, ExamCategory, Order, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'posted_by', 'created_at', 'answers']


class ExamCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCategory
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    category = ExamCategorySerializer()
    class Meta:
        model = Item
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    category = ExamCategorySerializer()
    class Meta:
        model = Item
        fields = ['id','category','title','description','og_price','price','is_free','pdf_file','thumbnail']

class ItemPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)
    class Meta:
        model = Order
        fields = '__all__'


class UnsubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # You can add additional email validation here if needed
        return value