from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
import razorpay
from django.db.models import F
from django.conf import settings
from main.models import *
from main.serializers import *
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
# Create your views here.

razorpay_api = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_KEY_SECRET)
)

MODEL_MAP = {
    "Books": (Book, BookSerializer),
    "Electronics": (Electronic, ElectronicSerializer),
    "Musical Instruments": (MusicalInstrument, MusicalInstrumentSerializer),
}

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # You can change this
    page_size_query_param = 'page_size'
    max_page_size = 100


class ItemGetAPI(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        category = request.GET.get("category")
        if category not in MODEL_MAP:
            return Response({"error": "Invalid or missing category"}, status=400)

        model_class, serializer_class = MODEL_MAP[category]
        queryset = model_class.objects.all()
        serializer = serializer_class(queryset, many=True)

        return Response({
            "category": category,
            "count": queryset.count(),
            "results": serializer.data
        }, status=200)

class ItemAllCategoryAPI(APIView):
    permission_classes = (AllowAny,)


    def get(self, request):

        books = Book.objects.all()
        electronics = Electronic.objects.all()
        instruments = MusicalInstrument.objects.all()

        results = []

        for item in books:
            results.append({
                "type": "Book",
                "data": BookSerializer(item).data
            })

        for item in electronics:
            results.append({
                "type": "Electronic",
                "data": ElectronicSerializer(item).data
            })

        for item in instruments:
            results.append({
                "type": "MusicalInstrument",
                "data": MusicalInstrumentSerializer(item).data
            })
        
        # Sort or shuffle if needed
        results = sorted(results, key=lambda x: x['data'].get('id', 0))

        # Paginate
        paginator = StandardResultsSetPagination()
        paginated_results = paginator.paginate_queryset(results, request)

        return paginator.get_paginated_response(paginated_results)


class ItemGetDetailAPI(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        id = request.GET.get('id')
        category = request.GET.get('category')

        if not id or category not in MODEL_MAP:
            return Response({'error': 'Please provide valid id and category.'}, status=400)

        model_class, serializer_class = MODEL_MAP[category]

        try:
            obj = model_class.objects.get(id=id)
        except model_class.DoesNotExist:
            return Response({'error': 'Item not found.'}, status=404)

        serializer = serializer_class(obj)
        return Response({
            "category": category,
            "data": serializer.data
        }, status=200)
        
        

class ItemPostAPI(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Book.objects.all()
    serializer_class = BookAddSerializer

class BookVariantAPI(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = BookVariant.objects.all()
    serializer_class = BookVariantSerializer

class ElectronicPostAPI(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Electronic.objects.all()
    serializer_class = ElectronicSerializer

class MusicalInstrumentPostAPI(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = MusicalInstrument.objects.all()
    serializer_class = MusicalInstrumentSerializer

class ElectronicVariantAPI(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ElectronicsVariant.objects.all()
    serializer_class = ElectronicVariantSerializer

class MusicalInstrumentVariantAPI(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = MusicalInstrumentVariant.objects.all()
    serializer_class = MusicalInstrumentVariantSerializer

class OrderViewSet(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name'] 

class SubCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name'] 

from main.services.cart_service import CartService

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)

    def post(self, request):
        category_id = request.data.get('category_id')
        variant_id = request.data.get('item_id')  # item_id is variant_id here

        if not category_id or not variant_id:
            return Response({'message': 'category_id and item_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # category model stays the same
        category = get_object_or_404(Category, id=category_id)

        try:
            order, message = CartService.add_item(request.user, category, variant_id)
        except ValueError as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': message, 'total_price': order.total_price}, status=status.HTTP_200_OK)

from main.services.cart_service import CartService

class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)

    def delete(self, request, item_id):
        """
        Now we only need item_id because CartService already knows the order.
        """
        if not item_id:
            return Response({'message': 'item_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = CartService.remove_item(request.user, item_id)
        except ValueError as e:
            return Response({'message': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Item removed from cart.', 'total_price': order.total_price},
                        status=status.HTTP_200_OK)

from main.services.payment_service import PaymentService

class CartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)

    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(user=request.user, payment_status=False).first()
        if not order:
            return Response({'message': 'No active order found.'}, status=status.HTTP_404_NOT_FOUND)

        items = order.items.all()
        serialized_items = ItemSerializer(items, many=True)

        # Create razorpay order through service
        razorpay_response = PaymentService.create_razorpay_order(order)
        order.razorpay_order_id = razorpay_response["id"]
        order.save()

        return Response({
            'items': serialized_items.data,
            'total_price': order.total_price,
            'item_count': items.count(),
            'razorpay_order_id': razorpay_response["id"],
            'razorpay_key_id': settings.RAZORPAY_API_KEY,
            'order_id': order.pk
        }, status=status.HTTP_200_OK)

from main.services.payment_service import PaymentService

class CheckoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(user=request.user, payment_status=False).first()
        if not order:
            return Response({'message': 'No active order found for checkout.'}, status=status.HTTP_404_NOT_FOUND)

        if not order.items.exists():
            return Response({'message': 'Your cart is empty. Add items to proceed to checkout.'},
                            status=status.HTTP_400_BAD_REQUEST)

        razorpay_response = PaymentService.create_razorpay_order(order)
        order.razorpay_order_id = razorpay_response["id"]
        order.save()
        serializer = self.get_serializer(order)

        return Response({
            'order': serializer.data,
            'razorpay_order_id': razorpay_response["id"],
            'razorpay_key_id': settings.RAZORPAY_API_KEY
        }, status=status.HTTP_200_OK)


from main.services.payment_service import PaymentService

class PaymentSuccessRazorpay(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def post(self, request):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        order_id = request.data.get('order_id')
        billing_address_id = request.data.get('billing_address_id')  # optional

        order = get_object_or_404(Order, user=request.user, payment_status=False, pk=order_id)
        billing_address = None
        if billing_address_id:
            billing_address = get_object_or_404(BillingAddress, pk=billing_address_id, user=request.user)

        PaymentService.mark_payment_success(order, razorpay_order_id, razorpay_payment_id, billing_address)

        return Response({'message': 'Payment Successful. Redirecting to Order Summary.'}, status=status.HTTP_200_OK)
class OrderHistory(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication)
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        return Order.objects.all()
    
    def get(self, request):
        queryset = self.get_queryset()
        data = queryset.filter(user=request.user,payment_status = True)
        paginator = self.pagination_class()
        result = paginator.paginate_queryset(data, request)
        serializer = OrderSerializer(result,many=True)
        return paginator.get_paginated_response(serializer.data)
class FilterItemsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ItemSerializer

    def get_queryset(self):
        """
        Optionally filters the items by category based on the 'category_id' parameter
        passed in the URL.
        """
        queryset = Book.objects.all()
        category_id = self.request.query_params.get('category', None)

        if category_id is not None:
            queryset = queryset.filter(category__id=category_id)
        
        return queryset

class SearchAPI(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = ItemSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__name', 'title','price']

class UnsubscribeView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UnsubscribeSerializer
    def post(self, request):
        serializer = UnsubscribeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # Check if the email is already unsubscribed
            if not UnsubscribedEmail.objects.filter(email=email).exists():
                UnsubscribedEmail.objects.create(email=email)
                return Response({'message': 'You have been successfully unsubscribed.'}, status=status.HTTP_200_OK)
            return Response({'message': 'Email is already unsubscribed.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAddressAPI(generics.ListCreateAPIView):
    queryset = BillingAddress.objects.all()
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    pagination_class = PageNumberPagination


class CategoryWiseProductList(APIView):
    permission_classes = (AllowAny,)

    class CustomPagination(PageNumberPagination):
        page_size = 12
        page_size_query_param = 'page_size'

    def get_serializer_class(self, category_name):
        if category_name == 'Books':
            return BookSerializer
        elif category_name == 'Electronics':
            return ElectronicSerializer
        elif category_name == 'Musical Instruments':
            return MusicalInstrumentSerializer
        return None

    def get_queryset(self, category, request):
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        is_paperback = request.GET.get('is_paperback')
        search = request.GET.get('q')
        sub_category = request.GET.get('sub_category')

        if category.name == 'Books':
            queryset = Book.objects.filter(category=category)
            if is_paperback in ['true', 'false']:
                queryset = queryset.filter(is_paperback=(is_paperback == 'true'))
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search)
                )
        elif category.name == 'Electronics':
            queryset = Electronic.objects.filter(category=category)
        elif category.name == 'Musical Instruments':
            queryset = MusicalInstrument.objects.filter(category=category)
        else:
            return []

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if sub_category:
            queryset = queryset.filter(sub_category__name=sub_category)

        if hasattr(queryset, 'order_by'):
            queryset = queryset.order_by('-updated_at')

        return queryset

    def get(self, request, categoryId: int):
        try:
            category = Category.objects.get(pk=categoryId)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset(category, request)
        serializer_class = self.get_serializer_class(category.name)

        if not serializer_class:
            return Response({"detail": "No serializer defined for this category."}, status=status.HTTP_400_BAD_REQUEST)

        paginator = self.CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = serializer_class(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

class ProductVariantCreateView(APIView):
    """
    Accepts multipart/form-data with product info and variant info.
    Creates base product if not exists, then creates variant.
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,SessionAuthentication)

    category_map = {
        'Books': Book,
        'Electronics': Electronic,
        'Musical Instruments': MusicalInstrument
    }

    category_variant_map = {
        'Books': BookVariant,
        'Electronics': ElectronicsVariant,
        'Musical Instruments': MusicalInstrumentVariant
    }

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        category_name = data['category']
        sub_category = data['sub_category']
        ProductModel = self.category_map.get(category_name)
        VariantModel = self.category_variant_map.get(category_name)

        if not ProductModel or not VariantModel:
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        # Try to find existing product by name & category
        product_qs = ProductModel.objects.filter(name=data['name'], category__name=category_name)
        if product_qs.exists():
            product = product_qs.first()
        else:
            # Create new product
            product_fields = {
                'name': data['name'],
                'category': product_qs.model.category.field.related_model.objects.get(name=category_name),
                'sub_category' : product_qs.model.sub_category.field.related_model.objects.get(id=sub_category),
                'description': data.get('description', ''),
                'price': data['price'],
                'stock': data['stock'],
                'image': data.get('image'),
            }

            # add book-specific fields
            if category_name == 'Books':
                product_fields.update({
                    'author': data.get('author', ''),
                    'isbn_10': data.get('isbn_10', ''),
                    'isbn_13': data.get('isbn_13', ''),
                    'edition': data.get('edition', ''),
                    'publisher': data.get('publisher', ''),
                    'publication_date': data.get('publication_date'),
                    'rating': data.get('rating', 5.0),
                })

            product = ProductModel.objects.create(**product_fields)

        # Create Variant
        variant_data = data['variant']
        if category_name == 'Books':
                variant = VariantModel.objects.create(
            product=product,
            stock=variant_data.get('stock', 0),
            price=variant_data.get('price'),
            color=variant_data.get('color'),
            image=variant_data.get('image'),
            
        
                format=variant_data.get('format', ''),
                is_free=variant_data.get('is_free', False),
                is_downloadable=variant_data.get('is_downloadable', True),
                sku=variant_data.get('sku'),
                pdf_file=variant_data.get('pdf_file')
            )
        else:
            variant = VariantModel.objects.create(
                product=product,
                stock=variant_data.get('stock', 0),
                price=variant_data.get('price'),
                color=variant_data.get('color'),
                image=variant_data.get('image')

                
            )

        return Response({
            "product_id": product.id,
            "variant_id": variant.id,
            "message": "Product & Variant saved successfully"
        }, status=status.HTTP_201_CREATED)
