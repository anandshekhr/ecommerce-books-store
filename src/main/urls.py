from django.urls import path, include
import main.views as views
from django.contrib import admin




urlpatterns = [ 
    path('login/', views.login_view, name='login-view'),
    path('logout/', views.logout_view, name='logout-view'),
    path('signup/', views.signup_view, name='signup-view'),
    
    # home page
    path('', views.item_list, name='home-1'),
    path('?subcategory=<str:subCategoryId>', views.category_wise_products, name='category-wise-products'),
    path('category/<int:categoryId>', views.category_wise_products, name='category-wise-products'),
    
    # product details
    path('product/<slug:category_slug>/<int:pk>/', views.product_detail, name='product-detail'),
    path('pdf/<hashid:item_id>/', views.view_pdf, name='view_pdf'),

    
    path('item/filter/', views.item_list_filter, name='item-filter'),
    path('item/search/', views.item_list_search, name='item-search'),
    path('cart/', views.view_cart, name='view_cart'),
    # path('add-to-cart/<hashid:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/add/<int:category_id>/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('order/history/', views.order_history, name='order-history'),
    path('view-pdf/<hashid:item_id>/', views.pdf_viewer, name='pdf_viewer'),
    path('order/summary/<hashid:pk>/', views.order_summary, name='order-summary'),
    # path('checkout/<hashid:order_id>/', views.checkout, name='checkout'),
    path('payment/success/',views.razorpay_success_redirect,name="razorpay-payment-success"),
    path('payment/phonepe/success/<hashid:order_id>/',views.phonepe_success_redirect,name="phonepe-payment-success"),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('refund-policy/', views.refund_policy, name='refund-policy'),
    path('shipping-policy/', views.shippping_policy, name='shipping-policy'),
    path('contact-us/', views.contact_us, name='contact-us'),
    path('questions/', views.question_list, name='question_list'),
    path('ask/', views.ask_question, name='ask_question'),
    path('answer/<hashid:question_id>/', views.answer_question, name='answer_question'),
    path('questions/<hashid:question_id>/', views.question_detail_view, name='question_detail'),
    path('questions/<hashid:question_id>/add_answer/', views.add_answer, name='add_answer'),
    path('pdf/serve/<int:pdf_id>/',views.serve_pdf,name="serve-pdf"),
    path('serve-pdf-page/<int:pdf_id>',views.serve_pdf_page,name="serve-pdf-page"),
    path('pdf/total-pages/<int:pdf_id>',views.totalPagePages,name="serve-pdf-page"),
    path('api/v1/billing-addresses/', views.billing_address_list, name='billing_address_list'),
    path('api/v1/billing-addresses/<int:address_id>/select/', views.select_billing_address, name='select_billing_address'),


    # admin
    path('educator/admin/products',views.adminProductList,name="educator-admin-products"),
    path('educator/admin/category',views.adminCategoryList,name="educator-admin-category"),
    path('educator/admin/add-product/', views.add_product, name='educator-admin-add-product'),
    path('educator/admin/earnings/', views.adminEarnings, name='educator-admin-earnings'),

    # api common


]

