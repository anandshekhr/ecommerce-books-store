# store/serializers.py

from rest_framework import serializers
from .models import *


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'posted_by', 'created_at', 'answers']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Book
        fields = ['id','category','title','description','og_price','price','is_free','pdf_file','thumbnail']

class ItemPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Book
        fields = '__all__'




class ItemOrderSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Book
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = ItemOrderSerializer(many=True)
    class Meta:
        model = Order
        fields = '__all__'


class UnsubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # You can add additional email validation here if needed
        return value

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields = '__all__'

class BookAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    def get_category_name(self, obj):
        return obj.category.name
    
    class Meta:
        model = Book
        fields = ['id', 'name', 'description', 'price','slug' ,'image','category','category_name','stock']

class BookVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookVariant
        fields = '__all__'

class ElectronicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electronic
        fields = ['id', 'name', 'description', 'price','slug', 'image','category','stock','brand','warranty_period','sub_category']
    
class ElectronicVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronicsVariant
        fields = '__all__'

class MusicalInstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicalInstrument
        fields = ['id', 'name', 'description', 'price','slug', 'image','category','stock']

class MusicalInstrumentVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicalInstrumentVariant
        fields = '__all__'

class ItemAllCategorySerializer(serializers.Serializer):
    type = serializers.CharField()
    data = serializers.DictField()