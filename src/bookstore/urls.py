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
from django.urls import path, include, register_converter
from main import views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .utils import HashIdConverter
from django.contrib.sitemaps.views import sitemap
from main.sitemaps import ProductSitemap
from django.conf.urls import handler404, handler500
from django.views.decorators.cache import cache_page

sitemaps = {
    'products': ProductSitemap,
}


register_converter(HashIdConverter, "hashid")


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

admin.site.site_header = "VAMS Book Store"
admin.site.index_title = "VAMS Book Store"
admin.site.site_title = "VAMS Book Store"


urlpatterns = [
    path('robots.txt', views.robots_txt),
    path('sitemap.xml', cache_page(0)(sitemap), {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('ebook/admin/', admin.site.urls),
    path('volt/', include('admin_volt.urls')),
    path('', include('main.urls')),
    path( API_URL +'search', views.SearchAPI.as_view()),
    path( API_URL +'cart', views.CartView.as_view()),
    path( API_URL +'order', views.OrderHistory.as_view()),
    path( API_URL +'items', views.ItemGetAPI.as_view()),
    path( API_URL +'items/detail', views.ItemGetDetailAPI.as_view()),
    path( API_URL +'items/add', views.ItemPostAPI.as_view()),
    path( API_URL +'list-items', views.FilterItemsView.as_view()),
    path( API_URL +'checkout', views.CheckoutView.as_view()),
    path( API_URL +'cart/add/<int:item_id>', views.AddToCartView.as_view()),
    path( API_URL +'cart/remove/<int:item_id>', views.RemoveFromCartView.as_view()),
    path( API_URL +'razorpay/confirm-payment', views.PaymentSuccessRazorpay.as_view()),
    path( API_URL, include(router.urls)),
    path( API_URL, include('middlewares.urls')),
    path( API_URL + 'accounts/', include('dj_rest_auth.urls')), 
    path( API_URL + 'accounts/register/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')), 
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# handler500 = "main.views.Error500"
# handler404 = "main.views.Error404"