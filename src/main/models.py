# store/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from django.utils import timezone
from decimal import Decimal

from django_quill.fields import QuillField

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='questions/images/', blank=True, null=True)
    document = models.FileField(upload_to='questions/documents/', blank=True, null=True)
    is_active = models.BooleanField(_("Is Active"),default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"Question: Id {self.pk}"
    
    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='answers/images/', blank=True, null=True)
    document = models.FileField(upload_to='answers/documents/', blank=True, null=True)
    is_active = models.BooleanField(_("Is Active"),default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"Answer Id: {self.pk}"
    
    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
    
    
class ExamCategory(models.Model):
    name = models.CharField(verbose_name=_("Category"),max_length=100)
    board = models.ForeignKey("self", verbose_name=_("Parent Category"), on_delete=models.CASCADE, default=None, null=True, blank=True)
    image = models.ImageField(_("image"), upload_to='image/',null=True, blank=True)

    def __str__(self):
        return f"{self.name} { '-' + self.board.name if self.board else ''}"
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Optional: You can also add a default boolean for marking a primary billing address
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name}, {self.city}, {self.country}"
    
    def save(self, *args, **kwargs):
        # If the address is marked as default, set other addresses of the same user to False
        if self.is_default:
            BillingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Billing Addresses"

class Item(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.SET_NULL, null=True,blank=True)
    category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    og_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=1.00)
    author = models.CharField(_("Author"), max_length=50, null=True,blank=True)
    isbn_10 = models.CharField(_("ISBN-10"), max_length=50, null=True,blank=True)
    isbn_13 = models.CharField(_("ISBN-13"), max_length=50, null=True,blank=True)
    edition = models.CharField(_("Edition"), max_length=50, null=True,blank=True)
    publisher = models.CharField(_("Publisher"), max_length=50, null=True,blank=True)
    publication_date = models.CharField(_("Publication Date"), max_length=50, null=True,blank=True)
    is_free = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=True)
    is_paperback = models.BooleanField(default=False)
    rating = models.DecimalField(_("Ratings"), max_digits=2, decimal_places=1, default=5.0)
    pdf_file = models.FileField(upload_to='pdfs/', max_length=500,null=True, blank=True)
    thumbnail = models.ImageField(_("thumbnail"), upload_to='thumbnails/',null=True, blank=True)
    is_available = models.BooleanField(default=True)
    variant = models.ForeignKey("self", verbose_name=_("Variant"), on_delete=models.SET_NULL, null=True,blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
    
    def get_absolute_url(self):
        return reverse('item-details', kwargs={'pk': self.pk})

class ProductImage(models.Model):
    product = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/',max_length=500)

    def __str__(self):
        return f"{self.product.title} Image"
    
    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(BillingAddress, verbose_name=_("billing address"), on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(Item)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default= 0.00)
    payment_status = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(_("RazorPay Order Id"), max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(_("RazorPay Payment Id"), max_length=500, null=True, blank=True)
    phonepe_id = models.CharField(_("PhonePe Payment Id"), max_length=100,null=True,blank=True)
    phonepe_merchant_transaction_id = models.CharField(_("PhonePe Transaction Id"),max_length=36,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

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


class LegalContent(models.Model):
    PAGE_CHOICES = [
        ('privacy_policy', 'Privacy Policy'),
        ('terms_of_service', 'Terms of Service'),
        ('refund_policy', 'Refund Policy'),
        ('shipping_policy', 'Shipping Policy'),
        ('contact_us', 'Contact Us'),
    ]

    page_type = models.CharField(max_length=50, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=100)
    content = QuillField()

    def __str__(self):
        return self.title

class PhonePePaymentRequestDetail(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.SET_NULL, blank=True, null=True)
    order_id = models.ForeignKey(Order, verbose_name=_("Order id"), on_delete=models.CASCADE,blank=True,null=True)
    amount = models.CharField(_("amount"), max_length=50,null=True,blank=True)
    success = models.BooleanField(_("Success"),default=False)
    code = models.CharField(_("Code"), max_length=50, blank=True, null=True)
    message = models.TextField(_("Message"))
    merchant_transaction_id = models.CharField(_("Merchant Transaction Id"), max_length=200,null=True, blank=True)
    transaction_id = models.CharField(_("Transaction Id"), max_length=200,null=True, blank=True)
    redirect_url = models.TextField(_("URL"))
    created_at = models.DateTimeField(_("created at"), auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = _("PhonePe Payment Detail")
        verbose_name_plural = _("PhonePe Payment Details")

    def __str__(self):
        return "Order Id: "

    def get_absolute_url(self):
        return reverse("PhonePePaymentDetail_detail", kwargs={"pk": self.pk})
    
    def get_order_sid(self):
        return self.order_id.sid

class UnsubscribedEmail(models.Model):
    email = models.EmailField(unique=True)
    unsubscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    

class Earning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE) 
    quantity_sold = models.PositiveIntegerField(default=0)
    total_earning = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    paid = models.BooleanField(_("Is Payment Released"),default=False)
    modified_at = models.DateTimeField(auto_now=True)  
    payment_date = models.DateField(null=True, blank=True) 

    def save(self, *args, **kwargs):
        self.total_earning = Decimal(self.item.price) * Decimal(self.quantity_sold) * Decimal(0.60)
        super().save(*args, **kwargs) 

    def __str__(self):
        return f"Earnings for {self.user} from {self.item} on {self.modified_at}"

