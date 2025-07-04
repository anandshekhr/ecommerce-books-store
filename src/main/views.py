# store/views.py

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect,JsonResponse
from .models import *
from .serializers import *
from django.contrib.auth.decorators import login_required
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from decimal import Decimal
from rest_framework import viewsets
from rest_framework.views import APIView
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
from .forms import ProductForm
from django.db.models import Q
import uuid
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.shortcuts import render


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
    categories = Category.objects.all()

    # Define category names to group (ensure these match your DB entries or slugs)
    category_mapping = {
        'Books': 'Books',
        'Electronics': 'Electronics',
        'Musical Instruments': 'Musical Instruments',
    }

    categorized_products = {}
    banners = Banner.objects.filter(active=True).order_by('-created_at')
    for display_name, category_name in category_mapping.items():
        category = Category.objects.filter(name__iexact=category_name).first()
        if category and display_name == 'Books':
            categorized_products[display_name] = Book.objects.filter(category=category).order_by('-updated_at')[:10]
        
        if category and display_name == 'Electronics':
            categorized_products[display_name] = Electronic.objects.filter(category=category).order_by('-updated_at')[:10]
        
        if category and display_name == 'Musical Instruments':
            categorized_products[display_name] = MusicalInstrument.objects.filter(category=category).order_by('-updated_at')[:10]

    return render(request, 'store/index.html', {
        'categories': categories,
        'categorized_products': categorized_products,
        'banners': banners,
    })

def category_wise_products(request, categoryId: int):
    category = Category.objects.get(pk=categoryId)
    context = {
        'category':category
    }
    return render(request, 'store/products_on_category.html', context=context)

def item_list_filter(request):
    category_id = request.GET.get('category')
    pcategory_id = request.GET.get('pcategory')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('q')

    items = Book.objects.filter(is_available=True)
    
    if category_id:
        category_obj = Category.objects.get(pk=category_id)
        items = items.filter(Q(category__id__icontains=category_obj.pk) |
                              Q(category__board__id__icontains=category_obj.pk))
    
    if pcategory_id:
        category_obj = Category.objects.get(pk=pcategory_id)
        items = items.filter(Q(category__id__icontains=category_obj.pk) |
                              Q(category__board__id__icontains=category_obj.pk))
    
    if search_query:
        items = items.filter(
        Q(title__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(price__icontains=search_query) |
        Q(category__name__icontains=search_query) | 
        Q(category__board__name__icontains=search_query) 
    )
    
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)

    # Pagination
    paginator = Paginator(items.order_by('-updated_at'), 9)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    return render(request, 'store/index.html', {'categories': categories, 'products': page_obj})

def item_list_search(request):
    search_query = request.GET.get('q')

    items = Book.objects.filter(is_available=True)
    
    if search_query:
        items = items.filter(
        Q(title__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(price__icontains=search_query) |
        Q(category__name__icontains=search_query) | 
        Q(category__board__name__icontains=search_query) 
    )

    # Pagination
    paginator = Paginator(items.order_by('-updated_at'), 9)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/product_list.html', {'products': page_obj,'item_length':len(items)})

def product_detail(request, category_slug, pk):
    category = get_object_or_404(Category, slug=category_slug)

    if category.name == 'Books':
        product = get_object_or_404(Book, pk=pk, category=category)
        relevant_products = Book.objects.filter(category=category).exclude(pk=pk)
    elif category.name == 'Electronics':
        product = get_object_or_404(Electronic, pk=pk, category=category)
        relevant_products = Electronic.objects.filter(category=category).exclude(pk=pk)
    elif category.name == 'Musical Instruments':
        product = get_object_or_404(MusicalInstrument, pk=pk, category=category)
        relevant_products = MusicalInstrument.objects.filter(category=category).exclude(pk=pk)
    else:
        product = None
        relevant_products = []

    return render(request, 'store/item.html', {
        'product': product,
        'category': category,
        'pdf_id': pk,
        'relevant_products': relevant_products
    })

@login_required(login_url='login-view')
def add_to_cart(request, category_id, item_id):
    category = get_object_or_404(Category, id=category_id)

    model_map = {
        'Books': Book,
        'Electronics': Electronic,
        'Musical Instruments': MusicalInstrument,
    }

    model = model_map.get(category.name)
    if not model:
        messages.error(request, "Unsupported product category.")
        return redirect('home-1')

    product = get_object_or_404(model, id=item_id)
    content_type = ContentType.objects.get_for_model(model)

    order, created = Order.objects.get_or_create(user=request.user, payment__status=False)
    # payment = Payment.objects.get_or_create(order=order,status=False)

    # Check if already in cart
    if order.items.filter(content_type=content_type, object_id=product.id).exists():
        messages.info(request, f'{product.name} already exists in the cart.')
        return redirect('view_cart')

    # Add item to cart
    OrderItem.objects.create(
        order=order,
        content_type=content_type,
        object_id=product.id,
        price_at_order_time=product.price,
        quantity=1
    )

    # Update order total
    order.update_total_price()

    messages.success(request, f'{product.name} successfully added to cart.')
    return redirect('view_cart')

@login_required(login_url='login-view')
def view_cart(request):
    try:
        address = BillingAddress.objects.get(user = request.user, is_default = True)
        # Try to get the user's active order (unpaid)
        order = Order.objects.get(user=request.user, payment__status= False)
        # Check if the order has any items
        if not order.items.exists():
            # If no items in the cart, display a message
            messages.warning(request, 'Your cart is empty. Please add items to your cart.')
            return render(request, 'store/cart.html', {
                'order': None,  # No active order with items
                'message': "Your cart is empty. Please add items to your cart."
            })
        request_data = {
            "amount": int(order.total_price * 100) if order.total_price > 1.00 else 100,
            "currency": "INR",
            "receipt": order.sid,
            }
        razorpay_response = razorpay_api.order.create(data=request_data)
        order.payment.razorpay_order_id = razorpay_response["id"]
        order.save()
        return render(request, 'store/cart.html', {'order': order,"billing_address":address,"razorpay_order_id": razorpay_response["id"],
                    "razorpay_key_id": settings.RAZORPAY_API_KEY,'total_amount':int(order.total_price) * 10000,'order_id':order.pk})
    except Order.DoesNotExist:
        # If no order exists, set order to None or an empty order object
        order = None  # You can customize this to fit your template logic
        return render(request, 'store/cart.html', {'order': order})

@login_required(login_url='login-view')
def order_summary(request, pk=None):
    orders = Order.objects.filter(user=request.user, payment__status=True)

    if pk:
        orders = orders.filter(pk=pk)

    return render(request, 'store/orders.html', {
        'orders': orders,
        'header': 'Order Summary' if pk else 'My Order History',
    })

@login_required(login_url='login-view')
def order_history(request):
    orders = Order.objects.filter(user=request.user,payment_status=True).order_by('-created_at')
    
    # Pagination: 10 orders per page
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/orders.html', {'orders': page_obj,'header':'Order History'})

@login_required(login_url='login-view')
def razorpay_success_redirect(request):
    razorpay_order_id = request.GET.get("razorpay_order_id")
    razorpay_payment_id = request.GET.get("razorpay_payment_id")
    order_id = request.GET.get('order_id')
    selected_billing_address = BillingAddress.objects.get(user=request.user, is_default=True)
    if request.user and order_id:
        order = Order.objects.get(user=request.user, payment__status=False,pk=order_id)
        order.payment.status = True
        order.payment.razorpay_payment_id = razorpay_payment_id
        order.payment.save()
        order.address = selected_billing_address

        order.save()

    messages.success(request, "Your order was successful!")
    return redirect("order-summary", pk=order.id)

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
    Book = get_object_or_404(Book, id=item_id, order=order)
    return render(request, 'store/view_pdf.html', {'pdf_file': Book.pdf_file.url})


class ItemGetAPI(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Book.objects.all()
    serializer_class = ItemSerializer

class ItemGetDetailAPI(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemSerializer

    def get(self, request):
        id = request.GET.get('id')
        if id:
            queryset = Book.objects.get(id=id)
            serializer = ItemSerializer(queryset)
            return Response(serializer.data,status=200)
        
        

class ItemPostAPI(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Book.objects.all()
    serializer_class = ItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AddToCartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)

    def post(self, request, item_id):
        Book = get_object_or_404(Book, id=item_id)
        order, created = Order.objects.get_or_create(user=request.user, payment_status=False)
        
        if order.items.filter(id=Book.id).exists():
            return Response({
                'message': 'Book is already in the cart','total_price': order.total_price
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.items.add(Book)
        total_price = Decimal(order.total_price) + Decimal(Book.price) if not Book.is_free else Decimal(0.00)
        order.total_price = total_price
        order.save()
        return Response({'message': 'Book added to cart','total_price': order.total_price}, status=status.HTTP_200_OK)

class RemoveFromCartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)


    def post(self, request, item_id):
        Book = get_object_or_404(Book, id=item_id)
        order = get_object_or_404(Order, user=request.user, payment_status=False)
        if Book in order.items.all():
            order.items.remove(Book)
            order.total_price -= Book.price if not Book.is_free else 0.00
            order.save()
            return Response({'message': 'Book removed from cart','total_price': order.total_price}, status=status.HTTP_200_OK)
        return Response({'message': 'Book not in cart','total_price': order.total_price}, status=status.HTTP_400_BAD_REQUEST)
    

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
    

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        #(email)
        #(password)
        user = authenticate(request, email=email, password=password)
        #(user)
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
            password = password
        
        #(email)
        #(password)
        
        # Generate a unique username
        username = generate_username(first_name, last_name)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'User already Exists with this email.')
            return redirect('signup-view')

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
        content = request.POST['content_html']
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
@csrf_exempt
def add_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        content = request.POST.get(f'content_html_{question_id}')
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
    Book = get_object_or_404(Book, id=item_id)
    last_page = request.session.get('pdf_last_page', 1)

    # If a new page number is posted (e.g., via AJAX), update the session
    if request.method == 'POST':
        page_number = request.POST.get('page_number')
        request.session['pdf_last_page'] = page_number
    
    if Book.pdf_file:
        context = {
            'pdf_url': Book.pdf_file.url,
            'last_page': last_page
        }
        return render(request, 'viewer/pdf_viewer.html', context)
    else:
        return render(request, 'error_page.html', {'message': 'PDF not found'})
    
@login_required
def serve_pdf(request, pdf_id):
    import os
    from django.http import FileResponse, Http404
    try:
        # Replace this with your logic to retrieve the PDF file
        pdf = get_object_or_404(Book, id=pdf_id)
        pdf_path = pdf.pdf_file.path  # Get file path of the PDF

        # Ensure the file exists
        if not os.path.exists(pdf_path):
            raise Http404("PDF file not found.")

        # Serve the PDF as a response
        response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{pdf.pdf_file.name}"'
        return response
    except Exception as e:
        raise Http404("PDF file not found.")

import PyPDF2
import os
def totalPagePages(request, pdf_id):
    """
    Serve a single page of the PDF and the total page count to the frontend.
    """
    pdf = get_object_or_404(Book, id=pdf_id)
    pdf_path = pdf.pdf_file.path 

    # Open the PDF and extract the specific page
    if os.path.exists(pdf_path):
        total_pages = 0
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)
            return JsonResponse({'total_pages':total_pages},status = status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "PDF not found"}, status=404)

def serve_pdf_page(request, pdf_id):
    """
    Serve a single page of the PDF and the total page count to the frontend.
    """
    try:
        page_num = int(request.GET.get('page', 1))
    except ValueError:
        page_num = 1
    pdf = get_object_or_404(Book, id=pdf_id)
    pdf_path = pdf.pdf_file.path 

    # Open the PDF and extract the specific page
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)

                if page_num <= total_pages:
                    page = pdf_reader.pages[page_num - 1]  # PyPDF2 is zero-indexed
                    output_pdf = PyPDF2.PdfWriter()
                    output_pdf.add_page(page)

                    response = HttpResponse(content_type="application/pdf")
                    output_pdf.write(response)
                    response['Content-Disposition'] = f'inline; filename="page-{page_num}.pdf"'
                    
                    # Set a custom header to include the total page count
                    response['X-Total-Pages'] = total_pages
                    return response
                else:
                    return JsonResponse({"error": "Page out of range"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "PDF not found"}, status=404)

def Error500(request):
    context = {
        'title':'Internal Server Error',
        'http_code': '500',
        'error_code': '-1'
    }
    return render(request, 'error/504.html',context,status=500)

def Error404(request):
    context = {
        'title':'Page Not Found',
        'http_code': '404',
        'error_code': '-1'
    }
    return render(request, 'error/504.html',context,status=404)


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


@login_required
def adminProductList(request):
    if request.user.is_staff:
        products = Book.objects.filter(user=request.user.id)
    else:
        products = []
        messages.error(request,'You donot have permission to view this page')
    return render(request, 'educator/products.html',{'products':products,'selected':'products'})

@login_required
def adminCategoryList(request):
    if request.user.is_staff:
        categories = Category.objects.all()

    else:
        categories = []
        messages.error(request,'You donot have permission to view this page')
    return render(request, 'educator/category.html',{'categories':categories,'selected':'category'})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            Book = form.save(commit=False)
            Book.user = request.user
            Book.save()
            return redirect('educator-admin-products')
    else:
        form = ProductForm()

    return render(request, 'educator/add_product.html', {'form': form,'selected':'add-products'})

@login_required
def adminEarnings(request):
    if request.user.is_staff:

        earning = Earning.objects.filter(user = request.user)
    else:
        earning = []
        messages.error('You are not authorized to view this page')
    return render(request, 'educator/earnings.html',{'earnings':earning,'selected':'earning'})

class UserAddressAPI(generics.ListCreateAPIView):
    queryset = BillingAddress.objects.all()
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    pagination_class = PageNumberPagination

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BillingAddress

@csrf_exempt
def billing_address_list(request):
    if request.method == 'GET':
        addresses = BillingAddress.objects.filter(user=request.user)
        data = [{"id": address.id, "full_name": address.full_name, "street_address": address.street_address, "city": address.city, "state": address.state, "postal_code": address.postal_code, "country": address.country} for address in addresses]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        data = request.POST
        # Convert 'is_default' from string to Boolean
        is_default = data.get('is_default', 'false').lower() == 'true'
        BillingAddress.objects.create(
            user=request.user,
            full_name=data['full_name'],
            street_address=data['street_address'],
            city=data['city'],
            state=data.get('state', ''),
            postal_code=data['postal_code'],
            country=data['country'],
            phone_number=data.get('phone_number', ''),
            is_default=is_default
        )
        return JsonResponse({'success': True})

@csrf_exempt
def select_billing_address(request, address_id):
    if request.method == 'POST':
        BillingAddress.objects.filter(user=request.user).update(is_default=False)
        BillingAddress.objects.filter(id=address_id, user=request.user).update(is_default=True)
        return JsonResponse({'success': True})


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
