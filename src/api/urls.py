from django.urls import path
from . import views

API_URL = 'api/v1/'

urlpatterns = [
    path( 'search', views.SearchAPI.as_view()),
    path( 'address', views.UserAddressAPI.as_view()),
    path( 'cart', views.CartView.as_view()),
    path( 'order', views.OrderHistory.as_view()),
    path( 'items', views.ItemGetAPI.as_view()),
    path( 'items/all', views.ItemAllCategoryAPI.as_view()),
    path( 'items/detail', views.ItemGetDetailAPI.as_view()),
    path( 'items/book/add', views.ItemPostAPI.as_view()),
    path( 'items/electronics/add', views.ElectronicPostAPI.as_view()),
    path( 'items/musical-instruments/add', views.MusicalInstrumentPostAPI.as_view()),
    path( 'list-items', views.FilterItemsView.as_view()),
    path( 'checkout', views.CheckoutView.as_view()),
    path( 'cart/add', views.AddToCartView.as_view(),name="add-to-cart-api"),
    path( 'cart/delete/<int:category_id>/<int:item_id>', views.RemoveFromCartView.as_view()),
    path( 'razorpay/confirm-payment', views.PaymentSuccessRazorpay.as_view()),
    path( 'unsubscribe/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    path( 'category/<int:categoryId>/items/', views.CategoryWiseProductList.as_view(), name='category-products-api'),


]
