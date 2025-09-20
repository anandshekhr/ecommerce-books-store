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
    category_name = serializers.SerializerMethodField()

    def get_category_name(self, obj):
        return obj.category.name
    class Meta:
        model = Electronic
        fields = ['id', 'name', 'description', 'price','slug', 'image','category','category_name','stock','brand','warranty_period','sub_category']
    
class ElectronicVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronicsVariant
        fields = '__all__'

class MusicalInstrumentSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    def get_category_name(self, obj):
        return obj.category.name
    class Meta:
        model = MusicalInstrument
        fields = ['id', 'name', 'description', 'price','slug', 'image','category','category_name','stock']

class MusicalInstrumentVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicalInstrumentVariant
        fields = '__all__'

class ItemAllCategorySerializer(serializers.Serializer):
    type = serializers.CharField()
    data = serializers.DictField()


class VariantSerializer(serializers.Serializer):
    format = serializers.CharField(required=False)
    is_free = serializers.BooleanField(default=False)
    is_downloadable = serializers.BooleanField(default=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    stock = serializers.IntegerField(default=0)
    sku = serializers.CharField(required=False)
    pdf_file = serializers.FileField(required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)

class ProductSerializer(serializers.Serializer):
    category = serializers.CharField()
    sub_category = serializers.IntegerField(required=True)
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField()
    slug = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)
    # Book specific:
    author = serializers.CharField(required=False, allow_blank=True)
    isbn_10 = serializers.CharField(required=False, allow_blank=True)
    isbn_13 = serializers.CharField(required=False, allow_blank=True)
    edition = serializers.CharField(required=False, allow_blank=True)
    publisher = serializers.CharField(required=False, allow_blank=True)
    publication_date = serializers.DateField(required=False, allow_null=True)
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, required=False)
    # Variant nested:
    variant = VariantSerializer()
