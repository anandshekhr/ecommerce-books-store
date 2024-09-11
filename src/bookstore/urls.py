"""
URL configuration for bookstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# pdf_ecommerce/urls.py

from django.contrib import admin
from django.urls import path, include
from main import views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


...

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


API_URL = 'api/v1/'


router = DefaultRouter()
router.register(r'orders', views.OrderViewSet)
router.register(r'categories', views.CategoryViewSet)


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('admin/', admin.site.urls),
    path('', views.item_list, name='home'),
    path('item/filter/', views.item_list_filter, name='item-filter'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('order/history/', views.order_history, name='order-history'),
    path('order/summary/<int:pk>/', views.order_summary, name='order-summary'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/success/',views.razorpay_success_redirect,name="razorpay-payment-success"),
    path('pdf/<int:item_id>/', views.view_pdf, name='view_pdf'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path( API_URL +'search', views.SearchAPI.as_view()),
    path( API_URL +'cart/', views.CartView.as_view()),
    path( API_URL +'items/', views.ItemGetAPI.as_view()),
    path( API_URL +'items/add/', views.ItemPostAPI.as_view()),
    path( API_URL +'list-items/', views.FilterItemsView.as_view()),
    path( API_URL +'checkout/', views.CheckoutView.as_view()),
    path( API_URL +'cart/add/<int:item_id>/', views.AddToCartView.as_view()),
    path( API_URL +'cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view()),
    path( API_URL, include(router.urls)),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
