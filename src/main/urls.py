from django.urls import path
import main.views as views

urlpatterns = [
    path('login/', views.login_view, name='login-view'),
    path('logout/', views.logout_view, name='logout-view'),
    path('signup/', views.signup_view, name='signup-view'),
    path('', views.item_list, name='home-1'),
    path('item/filter/', views.item_list_filter, name='item-filter'),
    path('item/<hashid:pk>/', views.product_detail, name='item-details'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<hashid:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('order/history/', views.order_history, name='order-history'),
    path('order/summary/<hashid:pk>/', views.order_summary, name='order-summary'),
    # path('checkout/<hashid:order_id>/', views.checkout, name='checkout'),
    path('payment/success/',views.razorpay_success_redirect,name="razorpay-payment-success"),
    path('payment/phonepe/success/<hashid:order_id>/',views.phonepe_success_redirect,name="phonepe-payment-success"),
    path('pdf/<hashid:item_id>/', views.view_pdf, name='view_pdf'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('refund-policy/', views.refund_policy, name='refund-policy'),
    path('shipping-policy/', views.shippping_policy, name='shipping-policy'),
    path('contact-us/', views.contact_us, name='contact-us'),
    path('questions/', views.question_list, name='question_list'),
    path('ask/', views.ask_question, name='ask_question'),
    path('answer/<int:question_id>/', views.answer_question, name='answer_question'),
    path('questions/<int:question_id>/', views.question_detail_view, name='question_detail'),
    path('questions/<int:question_id>/add_answer/', views.add_answer, name='add_answer'),
]