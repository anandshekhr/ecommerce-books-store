from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from main.models import Order, OrderItem, Payment, BillingAddress
from django.conf import settings
import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_KEY_SECRET))

class CartService:
    VARIANT_MODEL_MAP = {
        'Books': 'main.BookVariant',
        'Electronics': 'main.ElectronicsVariant',
        'Musical Instruments': 'main.MusicalInstrumentVariant',
    }

    @classmethod
    def add_item(cls, user, category, variant_id):
        variant_model_path = cls.VARIANT_MODEL_MAP.get(category.name)
        if not variant_model_path:
            raise ValueError("Unsupported product category")

        # dynamic import
        from django.apps import apps
        variant_model = apps.get_model(variant_model_path)
        variant = get_object_or_404(variant_model, id=variant_id)

        content_type = ContentType.objects.get_for_model(variant_model)
        order, created = Order.objects.get_or_create(user=user, payment_status=False)
        Payment.objects.get_or_create(order=order, defaults={'gateway': 'razorpay'})

        existing_item = order.items.filter(content_type=content_type, object_id=variant.id).first()
        if existing_item:
            existing_item.quantity += 1
            existing_item.save()
            message = f'{variant.product.name} quantity updated in the cart.'
        else:
            OrderItem.objects.create(
                order=order,
                content_type=content_type,
                object_id=variant.id,
                price_at_order_time=variant.price or 0,
                quantity=1
            )
            message = f'{variant.product.name} successfully added to cart.'

        order.update_total_price()
        return order, message

    @classmethod
    def remove_item(cls, user, item_id):
        order = Order.objects.filter(user=user, payment_status=False).first()
        if not order:
            raise ValueError("No active cart")

        order_item = get_object_or_404(order.items, id=item_id)
        order_item.delete()
        order.update_total_price()
        return order
