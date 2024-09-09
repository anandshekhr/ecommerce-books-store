# store/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from datetime import date


class ExamCategory(models.Model):
    name = models.CharField(max_length=100)
    board = models.CharField(_("Board"), max_length=500,null=True,blank=True)

    def __str__(self):
        return f"{self.name} - {self.board if self.board else ""}"

class Item(models.Model):
    category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    og_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pdf_file = models.FileField(upload_to='pdfs/')
    thumbnail = models.ImageField(_("thumbnail"), upload_to='thumbnails/',null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default= 0.00)
    payment_status = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(_("RazorPay Order Id"), max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(_("RazorPay Payment Id"), max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'
    
    def update_total_price(self):
        """
        Recalculate the total price of the order based on the price of each item.
        """
        total = 0
        for item in self.items.all():
            total += item.price
        self.total_price = total
        self.save()
    
    @property
    def sid(self):
        return "VAMS/{}/{}".format(date.today().strftime("%Y/%m%d"),self.id)
