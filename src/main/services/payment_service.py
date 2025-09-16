from django.conf import settings
import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_KEY_SECRET))

class PaymentService:
    @staticmethod
    def create_razorpay_order(order):
        amount = int(order.total_price * 100) if order.total_price > 1.00 else 100
        data = {
            "amount": amount,
            "currency": "INR",
            "receipt": order.sid,
        }
        return razorpay_client.order.create(data=data)

    @staticmethod
    def mark_payment_success(order, razorpay_order_id, razorpay_payment_id, billing_address):
        order.payment.status = True
        order.payment.razorpay_order_id = razorpay_order_id
        order.payment.razorpay_payment_id = razorpay_payment_id
        order.payment.gateway = 'razorpay'
        order.payment.save()
        order.address = billing_address
        order.payment_status = True
        order.save()
