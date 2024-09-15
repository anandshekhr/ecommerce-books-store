# store/views.py

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from .models import Item, ExamCategory, Order, LegalContent, PhonePePaymentRequestDetail, Question, Answer
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
from django.urls import reverse
import uuid
# from phonepe.sdk.pg.payments.v1.models.request.pg_pay_request import PgPayRequest
# from phonepe.sdk.pg.payments.v1.payment_client import PhonePePaymentClient
# from phonepe.sdk.pg.env import Env
from django.views.decorators.csrf import csrf_protect,csrf_exempt



# s2s_callback_url = settings.PAYMENT_SUCCESS_REDIRECT_URL
# id_assigned_to_user_by_merchant = settings.PHONEPE_USER_ID


stripe.api_key = settings.STRIPE_SECRET_KEY
razorpay_api = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_KEY_SECRET)
)

# merchant_id = settings.PHONEPE_MERCHANT_ID
# salt_key = settings.PHONEPE_SALT_KEY
# salt_index = 1
# env = Env.UAT # Change to Env.PROD when you go live

# phonepe_client = PhonePePaymentClient(
#     merchant_id=merchant_id, salt_key=salt_key, salt_index=salt_index, env=env
# )
from django.core.paginator import Paginator

def privacy_policy(request):
    policy = get_object_or_404(LegalContent, page_type='privacy_policy')
    return render(request, 'policies/legal_content.html', {'content': policy})

def terms_of_service(request):
    terms = get_object_or_404(LegalContent, page_type='terms_of_service')
    return render(request, 'policies/legal_content.html', {'content': terms})

def refund_policy(request):
    terms = get_object_or_404(LegalContent, page_type='refund_policy')
    return render(request, 'policies/legal_content.html', {'content': terms})

def shippping_policy(request):
    terms = get_object_or_404(LegalContent, page_type='shipping_policy')
    return render(request, 'policies/legal_content.html', {'content': terms})

def contact_us(request):
    terms = get_object_or_404(LegalContent, page_type='contact_us')
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
    pcategory_id = request.GET.get('pcategory')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('q')

    items = Item.objects.filter(is_available=True)
    
    if category_id:
        category_obj = ExamCategory.objects.get(pk=category_id)
        items = items.filter(category=category_obj)
    
    if pcategory_id:
        category_obj = ExamCategory.objects.get(pk=pcategory_id)
        items = items.filter(category__board=category_obj)
    
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

def product_detail(request, pk):
    product = get_object_or_404(Item, pk=pk)
    return render(request, 'store/item.html', {'product': product,'pdf_url': product.pdf_file.url})

@login_required(login_url='login-view')
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    order, created = Order.objects.get_or_create(user=request.user, payment_status=False)
    if order.items.filter(id=item.id).exists():
        messages.info(request,'Item already exists in the cart.')
        return redirect('home-1')
        
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

def order_summary(request, pk=None):
    if pk:
        orders = Order.objects.filter(user=request.user, payment_status=True,pk=pk)
        
    else:
        orders = None
    return render(request, 'store/orders.html', {'orders': orders,'header':'Order Summary'})

@login_required(login_url='login-view')
def order_history(request):
    orders = Order.objects.filter(user=request.user,payment_status=True).order_by('-created_at')
    
    # Pagination: 10 orders per page
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/orders.html', {'orders': page_obj,'header':'Order History'})

# @login_required(login_url='login-view')
# def checkout(request,order_id):
#     order = get_object_or_404(Order, user=request.user, payment_status=False, pk=order_id)
#     request_data = {
#     "amount": int(order.total_price * 100),
#     "currency": "INR",
#     "receipt": order.sid,
#     }
#     razorpay_response = razorpay_api.order.create(data=request_data)
#     order.razorpay_order_id = razorpay_response["id"]
#     # Phone pe
#     unique_transaction_id = str(uuid.uuid4())
#     order.phonepe_merchant_transaction_id = unique_transaction_id
#     order.save()

#     pay_page_request = PgPayRequest.pay_page_pay_request_builder(
#         merchant_transaction_id=unique_transaction_id,
#         amount=int(order.total_price * 100),
#         merchant_user_id=id_assigned_to_user_by_merchant,
#         merchant_order_id=order.sid,
#         redirect_mode="POST",
#         callback_url=request.build_absolute_uri(reverse('phonepe-payment-success', kwargs={'order_id': order.id})),
#         # redirect_mode="REDIRECT",
#         redirect_url=request.build_absolute_uri(reverse('phonepe-payment-success', kwargs={'order_id': order.id})),
#     )
#     pay_page_response = phonepe_client.pay(pay_page_request)
#     pay_page_url = pay_page_response.data.instrument_response.redirect_info.url

#     if pay_page_url:
#         # Add Payment Details
#         phonepe_transaction_record = PhonePePaymentRequestDetail()
#         phonepe_transaction_record.user = request.user
#         phonepe_transaction_record.order_id = order
#         phonepe_transaction_record.amount = order.total_price
#         phonepe_transaction_record.success = pay_page_response.success
#         phonepe_transaction_record.code = pay_page_response.code
#         phonepe_transaction_record.message = pay_page_response.message
#         phonepe_transaction_record.merchant_transaction_id = (
#             pay_page_response.data.merchant_transaction_id
#         )
#         phonepe_transaction_record.transaction_id = (
#             pay_page_response.data.transaction_id
#         )
#         phonepe_transaction_record.redirect_url = pay_page_url
#         phonepe_transaction_record.save()


#     return redirect(pay_page_url)

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

@csrf_exempt
def phonepe_success_redirect(request, order_id):
    # order_id = request.GET.get('order_id')
    if order_id:
        order = Order.objects.get(payment_status=False,pk=order_id)
        order.payment_status = True
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
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home-1')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'accounts/login.html')

def generate_username(first_name, last_name):
    base_username = f"{first_name.lower()}.{last_name.lower()}"
    username = base_username
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{generate_random_number()}"
    return username

import random
import string
def generate_random_number(length=4):
    return ''.join(random.choices(string.digits, k=length))

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password = request.POST['password']

        if first_name:
            first_name = first_name.strip()
        
        if last_name:
            last_name = last_name.strip()
        
        if email:
            email = email.strip()
        
        if phone_number:
            phone_number = phone_number.strip()
        
        if password:
            password = password.strip()
        
        # Generate a unique username
        username = generate_username(first_name, last_name)

        # Create a new user
        user = User.objects.create_user(email=email,username=username, first_name=first_name, last_name=last_name +";"+phone_number , password=password)
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login-view')
    return render(request, 'accounts/login.html')

login_required(login_url='login-view')
def logout_view(request):
    # Log the user out
    logout(request)
    
    # Redirect to the login page or any other page
    return redirect('home-1')


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /",
        "Sitemap: http://www.vamsbookstore.in/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


@login_required
def question_list(request):
    # Get filter and search parameters
    user_filter = request.GET.get('user', None)
    search_query = request.GET.get('search', '')

    questions = Question.objects.all()

    # Filter by logged-in user if user_filter is provided
    if user_filter == 'me' and request.user.is_authenticated:
        questions = questions.filter(user=request.user)
    
    # Search functionality
    if search_query:
        questions = questions.filter(content__icontains=search_query)

    # Limit answers to the most recent 5
    for question in questions:
        question.answers_list = question.answers.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'questions': questions,
        'search_query': search_query,
    }
    return render(request, 'qa/questions_list.html', context)

@login_required
def ask_question(request):
    if request.method == 'POST':
        content = request.POST['content']
        image = request.FILES.get('image')
        document = request.FILES.get('document')

        question = Question.objects.create(user=request.user, content=content, image=image, document=document)
        return redirect('question_list')
    
    return render(request, 'qa/ask_question.html')

@login_required
def answer_question(request, question_id):
    question = Question.objects.get(id=question_id)
    if request.method == 'POST':
        content = request.POST['content']
        image = request.FILES.get('image')
        document = request.FILES.get('document')

        Answer.objects.create(user=request.user, question=question, content=content, image=image, document=document, is_active=True)
        return redirect('question_list')
    
    return render(request, 'qa/answer_question.html', {'question': question})


def question_detail_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.answers_list = question.answers.filter(is_active = True)
    # answers = answers.filter(is_active = True)
    context = {
        'question': question,
        # 'answers': answers,
    }
    return render(request, 'qa/question_detail.html', context)

# Add new answer to a question
def add_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        document = request.FILES.get('document')
        Answer.objects.create(content=content, user=request.user, image=image, document=document,question=question)
        # Redirect to the referring page or default to the question detail page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return HttpResponseRedirect(referer)
        else:
            return redirect('question_detail', question_id=question.id)

def pdf_viewer(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    last_page = request.session.get('pdf_last_page', 1)

    # If a new page number is posted (e.g., via AJAX), update the session
    if request.method == 'POST':
        page_number = request.POST.get('page_number')
        request.session['pdf_last_page'] = page_number
    
    if item.pdf_file:
        context = {
            'pdf_url': item.pdf_file.url,
            'last_page': last_page
        }
        return render(request, 'viewer/pdf_viewer.html', context)
    else:
        return render(request, 'error_page.html', {'message': 'PDF not found'})