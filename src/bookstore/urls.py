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

API_URL = 'api/v1/'


router = DefaultRouter()
router.register(r'items', views.ItemViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'categories', views.CategoryViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.item_list, name='item_list'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('pdf/<int:item_id>/', views.view_pdf, name='view_pdf'),
    path( API_URL +'search', views.SearchAPI.as_view()),
    path( API_URL +'cart/', views.CartView.as_view()),
    path( API_URL +'list-items', views.FilterItemsView.as_view()),
    path( API_URL +'checkout/', views.CheckoutView.as_view()),
    path( API_URL +'cart/add/<int:item_id>/', views.AddToCartView.as_view()),
    path( API_URL +'cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view()),
    path( API_URL, include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
