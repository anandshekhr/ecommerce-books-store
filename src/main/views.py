# store/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, ExamCategory, Order, LegalContent
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
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
import razorpay
from datetime import datetime
from django.contrib import auth, messages
from decimal import Decimal
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


stripe.api_key = settings.STRIPE_SECRET_KEY
razorpay_api = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_KEY_SECRET)
)
from django.core.paginator import Paginator

def privacy_policy(request):
    policy = get_object_or_404(LegalContent, page_type='privacy_policy')
    return render(request, 'policies/legal_content.html', {'content': policy})

def terms_of_service(request):
    terms = get_object_or_404(LegalContent, page_type='terms_of_service')
    return render(request, 'policies/legal_content.html', {'content': terms})


def item_list(request):
    categories = ExamCategory.objects.all()
    items = Item.objects.filter(is_available=True)
    selected_category = request.GET.get('category')
    if selected_category:
        items = items.filter(category_id=selected_category)

    # Pagination
    paginator = Paginator(items.order_by('id'), 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/index.html', {'categories': categories, 'products': page_obj})

def item_list_filter(request):
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('q')

    items = Item.objects.filter(is_available=True)
    
    if category_id:
        category_obj = ExamCategory.objects.get(pk=category_id)
        items = items.filter(category=category_obj)
    
    if search_query:
        items = items.filter(title__icontains=search_query)
    
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)

    # Pagination
    paginator = Paginator(items.order_by('id'), 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ExamCategory.objects.all()
    return render(request, 'store/index.html', {'categories': categories, 'products': page_obj})

@login_required(login_url='login-view')
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    order, created = Order.objects.get_or_create(user=request.user, payment_status=False)
    if order.items.filter(id=item.id).exists():
        messages.info(request,'Item already exists in the cart.')
        return redirect('home')
        
    order.items.add(item)
    order.total_price = Decimal(item.price) + Decimal(order.total_price)
    order.save()
    messages.info(request,'Item successfully added to cart.')
    return redirect('view_cart')

@login_required(login_url='login-view')
def view_cart(request):
    try:
        # Try to get the user's active order (unpaid)
        order = Order.objects.get(user=request.user, payment_status=False)
        # Check if the order has any items
        if not order.items.exists():
            # If no items in the cart, display a message
            messages.warning(request, 'Your cart is empty. Please add items to your cart.')
            return render(request, 'store/cart.html', {
                'order': None,  # No active order with items
                'message': "Your cart is empty. Please add items to your cart."
            })
        request_data = {
            "amount": int(order.total_price * 100),
            "currency": "INR",
            "receipt": order.sid,
            }
        razorpay_response = razorpay_api.order.create(data=request_data)
        order.razorpay_order_id = razorpay_response["id"]
        order.save()
        return render(request, 'store/cart.html', {'order': order,"razorpay_order_id": razorpay_response["id"],
                    "razorpay_key_id": settings.RAZORPAY_API_KEY,'total_amount':int(order.total_price) * 10000,'order_id':order.pk})
    except Order.DoesNotExist:
        # If no order exists, set order to None or an empty order object
        order = None  # You can customize this to fit your template logic
        return render(request, 'store/cart.html', {'order': order})

@login_required(login_url='login-view')
def order_summary(request, pk=None):
    if pk:
        orders = Order.objects.filter(user=request.user, payment_status=True,pk=pk)
    else:
        orders = None
    return render(request, 'store/orders.html', {'orders': orders})

@login_required(login_url='login-view')
def order_history(request):
    orders = Order.objects.filter(user=request.user, payment_status=True)
    return render(request, 'store/orders.html', {'orders': orders})

@login_required(login_url='login-view')
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
                   "razorpay_key_id": settings.RAZORPAY_API_KEY,'total_amount':int(order.total_price) * 10000,'order_id':order.pk})

@login_required(login_url='login-view')
def razorpay_success_redirect(request):
    razorpay_order_id = request.GET.get("razorpay_order_id")
    razorpay_payment_id = request.GET.get("razorpay_payment_id")
    order_id = request.GET.get('order_id')
    if request.user and order_id:
        order = Order.objects.get(user=request.user, payment_status=False,pk=order_id)
        order.payment_status = True
        order.razorpay_payment_id = razorpay_payment_id
        order.save()

    messages.success(request, "Your order was successful!")
    return redirect("order-summary", pk=order.id)


@login_required(login_url='login-view')
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
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)

    def post(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        order, created = Order.objects.get_or_create(user=request.user, payment_status=False)
        
        if order.items.filter(id=item.id).exists():
            return Response({
                'message': 'Item is already in the cart','total_price': order.total_price
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.items.add(item)
        total_price = Decimal(order.total_price) + Decimal(item.price)
        order.total_price = total_price
        order.save()
        return Response({'message': 'Item added to cart','total_price': order.total_price}, status=status.HTTP_200_OK)

class RemoveFromCartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)


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
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)


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
        queryset = Item.objects.all()
        category_id = self.request.query_params.get('category', None)

        if category_id is not None:
            queryset = queryset.filter(category__id=category_id)
        
        return queryset

class SearchAPI(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__name', 'title','price']
    



def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password = request.POST['password']

        # Create a new user
        user = User.objects.create_user(username=email, first_name=first_name, last_name=last_name, password=password)
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login-view')
    return render(request, 'accounts/login.html')

login_required(login_url='login-view')
def logout_view(request):
    # Log the user out
    logout(request)
    
    # Redirect to the login page or any other page
    return redirect('home')