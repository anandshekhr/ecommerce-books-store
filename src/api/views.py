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
    serializer_class = ItemSerializer

class ElectronicPostAPI(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Electronic.objects.all()
    serializer_class = ElectronicSerializer

class MusicalInstrumentPostAPI(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = MusicalInstrument.objects.all()
    serializer_class = MusicalInstrumentSerializer

class OrderViewSet(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)

    def post(self, request):
        category_id = request.data.get('category_id',None)
        item_id = request.data.get('item_id',None)
        quantity = request.data.get('quantity',None)

        category = get_object_or_404(Category, id=category_id)

        model, serializer = MODEL_MAP.get(category.name)
        if not model:
            return Response({'message':'Invalid category.'}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(model, id=item_id)
        content_type = ContentType.objects.get_for_model(model)
        order, created = Order.objects.get_or_create(user=request.user, payment_status=False)
        payment = Payment.objects.get_or_create(order=order,status=False)
        
        if order.items.filter(content_type=content_type, object_id=product.id).exists():
            updated_count = OrderItem.objects.filter(
                order=order,
                content_type=content_type,
                object_id=product.id
            ).update(quantity=quantity if quantity else F('quantity') + 1)
        else:
            # Add item to cart
            OrderItem.objects.create(
                order=order,
                content_type=content_type,
                object_id=product.id,
                price_at_order_time=product.price,
                quantity= quantity if quantity else 1
            )
        # Update order total
        order.update_total_price()
        return Response({'message': f'{product.name} added to cart','total_price': order.total_price}, status=status.HTTP_200_OK)

class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)

    def delete(self, request, category_id, item_id):

        if not category_id or not item_id:
            return Response({'message': 'category_id and item_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        category = get_object_or_404(Category, id=category_id)

        model, serializer = MODEL_MAP.get(category.name)
        if not model:
            return Response({'message': 'Invalid category.'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(model, id=item_id)
        content_type = ContentType.objects.get_for_model(model)

        try:
            order = Order.objects.get(user=request.user, payment_status=False)
        except Order.DoesNotExist:
            return Response({'message': 'No active cart found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            order_item = OrderItem.objects.get(order=order, content_type=content_type, object_id=product.id)
        except OrderItem.DoesNotExist:
            return Response({'message': f'{product.name} not in cart.'}, status=status.HTTP_400_BAD_REQUEST)

        order_item.delete()

        # Update order total
        order.update_total_price()

        return Response({'message': f'{product.name} removed from cart.', 'total_price': order.total_price}, status=status.HTTP_204_NO_CONTENT)

    

class CartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)


    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, payment_status=False)
            items = order.items.all()
            total_price = order.total_price
            item_count = items.count()

            # Serialize the Book data
            serialized_items = ItemSerializer(items, many=True)

            #razorpay

            request_data = {
            "amount": int(order.total_price * 100) if int(order.total_price) > 0 else 100,
            "currency": "INR",
            "receipt": order.sid,
            }
            razorpay_response = razorpay_api.order.create(data=request_data)
            order.razorpay_order_id = razorpay_response["id"]
            order.save()

            return Response({
                'items': serialized_items.data,
                'total_price': total_price,
                'item_count': item_count,
                "razorpay_order_id": razorpay_response["id"],
                "razorpay_key_id": settings.RAZORPAY_API_KEY,
                "order_id":order.pk
            }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({
                'message': 'No active order found.'
            }, status=status.HTTP_404_NOT_FOUND)

# store/api_views.py
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


class CheckoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)

    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        try:
            # Get the user's current order
            order = Order.objects.get(user=request.user, payment_status=False)

            # Ensure there are items in the cart before proceeding to checkout
            if not order.items.exists():
                return Response({
                    'message': 'Your cart is empty. Add items to proceed to checkout.'
                }, status=status.HTTP_400_BAD_REQUEST)

            request_data = {
            "amount": int(order.total_price * 100),
            "currency": "INR",
            "receipt": order.sid,
            }
            razorpay_response = razorpay_api.order.create(data=request_data)
            order.razorpay_order_id = razorpay_response["id"]
            order.save()
            serializer = self.get_serializer(order)

            
            return Response({'order': serializer.data ,"razorpay_order_id": razorpay_response["id"],
                   "razorpay_key_id": settings.RAZORPAY_API_KEY}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({
                'message': 'No active order found for checkout.'
            }, status=status.HTTP_404_NOT_FOUND)


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

class PaymentSuccessRazorpay(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    def post(self,request):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        order_id = request.data.get('order_id')
        if order_id:
            order_id = int(order_id)
        order = Order.objects.get(user=request.user, payment_status=False,pk=order_id)
        order.payment_status = True
        order.razorpay_payment_id = razorpay_payment_id
        order.save()
        return Response({'message':'Payment Successful. Redirecting to Order Summary.'})