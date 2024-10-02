from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import Order, Earning, Item
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timezone import make_aware
from decimal import Decimal

class Command(BaseCommand):
    help = 'Update earnings based on paid orders and purchased items'

    def handle(self, *args, **kwargs):
        now = datetime.now()
        today = make_aware(now).date()
        
        # 1. Fetch all paid orders from today
        paid_orders = Order.objects.filter(payment_status=True, updated_at__date=today)

        if not paid_orders.exists():
            self.stdout.write(self.style.SUCCESS(f'No paid orders for {today}.'))
            return
        
        # 2. Iterate through each paid order
        for order in paid_orders:
            for item_order in order.items.all():
                # Fetch the item and its owner
                item = item_order
                owner = item.user 
                
                # 3. Check if there's already an earning record for this user and item
                earning, created = Earning.objects.get_or_create(
                    user=owner,
                    item=item,
                    paid=False  # Assuming earnings will be marked as 'Pending' until payment is confirmed
                )
                
                # 4. Update the number of items sold
                earning.quantity_sold += 1
                earning.total_earning = Decimal(earning.item.price) * Decimal(earning.quantity_sold) * Decimal(0.60)
                
                # 5. Save the updated earning record
                earning.save()
                
                self.stdout.write(self.style.SUCCESS(f'Updated earnings for user {owner.username} for item {item.title}.'))

        self.stdout.write(self.style.SUCCESS(f'Earnings updated successfully for all paid orders on {today}.'))
