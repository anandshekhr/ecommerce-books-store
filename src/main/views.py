# store/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, ExamCategory, Order
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from decimal import Decimal
from rest_framework import viewsets
from .models import Item, Order
from .serializers import ItemSerializer, OrderSerializer, ExamCategorySerializer
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
import razorpay
from datetime import datetime
from django.contrib import auth, messages


stripe.api_key = settings.STRIPE_SECRET_KEY
razorpay_api = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_KEY_SECRET)
)

def item_list(request):
    categories = ExamCategory.objects.all()
    items = Item.objects.filter(is_available=True)
    selected_category = request.GET.get('category')
    if selected_category:
        items = items.filter(category_id=selected_category)
    return render(request, 'store/item_list.html', {'categories': categories, 'items': items})

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    order, created = Order.objects.get_or_create(user=request.user, payment_status=False)
    order.items.add(item)
    order.total_price += item.price
    order.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    order = get_object_or_404(Order, user=request.user, payment_status=False)
    return render(request, 'store/cart.html', {'order': order})

@login_required
def checkout(request):
    order = get_object_or_404(Order, user=request.user, payment_status=False)
    request_data = {
    "amount": int(order.total_price * 100),
    "currency": "INR",
    "receipt": order.sid,
    }
    razorpay_response = razorpay_api.order.create(data=request_data)
    order.razorpay_order_id = razorpay_response["id"]
    order.save()

    return render(request, 'store/checkout.html', 
                  {'order': order,"razorpay_order_id": razorpay_response["id"],
                   "razorpay_key_id": settings.RAZORPAY_API_KEY})

@login_required()
def razorpay_success_redirect(request):
    razorpay_order_id = request.GET.get("razorpay_order_id")
    razorpay_payment_id = request.GET.get("razorpay_payment_id")
    if request.user:
        order = Order.objects.get(user=request.user, payment_status=False)

        order.payment_status = True
        order.razorpay_payment_id = razorpay_payment_id
        order.save()

    messages.success(request, "Your order was successful!")
    return redirect("ordersummary", pk=order.id)


@login_required
def view_pdf(request, item_id):
    order = get_object_or_404(Order, user=request.user, payment_status=True)
    item = get_object_or_404(Item, id=item_id, order=order)
    return render(request, 'store/view_pdf.html', {'pdf_file': item.pdf_file.url})


class ItemGetAPI(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class ItemPostAPI(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = ExamCategory.objects.all()
    serializer_class = ExamCategorySerializer


class AddToCartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        order, created = Order.objects.get_or_create(user=request.user, payment_status=False)
        
        if order.items.filter(id=item.id).exists():
            return Response({
                'message': 'Item is already in the cart','total_price': order.total_price
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.items.add(item)
        order.total_price += Decimal(item.price)
        order.save()
        return Response({'message': 'Item added to cart','total_price': order.total_price}, status=status.HTTP_200_OK)

class RemoveFromCartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        order = get_object_or_404(Order, user=request.user, payment_status=False)
        if item in order.items.all():
            order.items.remove(item)
            order.total_price -= item.price
            order.save()
            return Response({'message': 'Item removed from cart','total_price': order.total_price}, status=status.HTTP_200_OK)
        return Response({'message': 'Item not in cart','total_price': order.total_price}, status=status.HTTP_400_BAD_REQUEST)
    

class CartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, payment_status=False)
            items = order.items.all()  # Get all items in the current order
            total_price = order.total_price
            item_count = items.count()

            # Serialize the item data
            serialized_items = ItemSerializer(items, many=True)

            return Response({
                'items': serialized_items.data,
                'total_price': total_price,
                'item_count': item_count
            }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({
                'message': 'No active order found.'
            }, status=status.HTTP_404_NOT_FOUND)

# store/api_views.py

class CheckoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
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
        queryset = Item.objects.all()
        category_id = self.request.query_params.get('category_id', None)

        if category_id is not None:
            queryset = queryset.filter(category__id=category_id)
        
        return queryset

class SearchAPI(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__name', 'title','price']
    