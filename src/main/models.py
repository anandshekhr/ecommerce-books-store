# store/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from django.utils import timezone
from decimal import Decimal
from django_quill.fields import QuillField
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify

import uuid
import random
import string

def generate_sku(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique SKU string.

    :param prefix: Optional prefix for the SKU (e.g., category code like "ELEC").
    :param length: Length of the random alphanumeric part.
    :return: SKU string like "ELEC-AB12CD34".
    """
    # Generate random uppercase letters + digits
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if prefix:
        return f"{prefix}-{random_part}"
    return random_part


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

# ---------- CATEGORY & SUBCATEGORY ----------

class Category(models.Model):
    name = models.CharField(verbose_name=_("Category"), max_length=100)
    image = models.ImageField(_("Image"), upload_to='image/', null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=120, verbose_name=_("Slug"),null=True,blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Automatically generate slug from name if not provided
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class SubCategory(models.Model):
    name = models.CharField(_("SubCategory"), max_length=50)
    parent_category = models.ForeignKey(Category, verbose_name=_("Category"), on_delete=models.CASCADE)
    image = models.ImageField(_("Image"), upload_to='image/subcategory/', null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=120, verbose_name=_("Slug"),null=True,blank=True)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Automatically generate slug from name if not provided
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("SubCategory_detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = _("SubCategory")
        verbose_name_plural = _("SubCategories")


class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, max_length=120, verbose_name=_("Slug"),null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Automatically generate slug from name if not provided
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# ---------- PRODUCT IMAGES ----------

class ProductImage(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')

    image = models.ImageField(upload_to='item_images/', max_length=500)

    def __str__(self):
        return f"{self.product.name} Image"

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
    
# ---------- ABSTRACT PRODUCT MODEL ----------
class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, verbose_name=_("Category"), on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    slug = models.SlugField(unique=True, max_length=120, verbose_name=_("Slug"),null=True,blank=True)

    image = models.ImageField(upload_to='products/')
    images = GenericRelation(ProductImage, related_query_name='images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Automatically generate slug from name if not provided
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


# ---------- BOOK PRODUCT ----------

class Book(Product):
    sub_category = models.ForeignKey(SubCategory, related_name="books_category", on_delete=models.CASCADE, null=True, blank=True, default="")
    author = models.CharField(_("Author"), max_length=100, blank=True)
    isbn_10 = models.CharField(_("ISBN-10"), max_length=20, blank=True)
    isbn_13 = models.CharField(_("ISBN-13"), max_length=20, blank=True)
    edition = models.CharField(_("Edition"), max_length=50, blank=True)
    publisher = models.CharField(_("Publisher"), max_length=100, blank=True)
    publication_date = models.CharField(_("Publication Date"), max_length=50, blank=True)
    rating = models.DecimalField(_("Ratings"), max_digits=2, decimal_places=1, default=5.0)

    def __str__(self):
        return f"{self.name} - {self.author} - {self.sub_category.name}"


class BookVariant(models.Model):
    product = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='variants')
    format = models.CharField(_("Format"), max_length=50, choices=[
        ('ebook', 'eBook'),
        ('paperback', 'Paperback'),
        ('hardcover', 'Hardcover'),
    ])
    is_free = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True,null=True,blank=True)
    pdf_file = models.FileField(upload_to='pdfs/', max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='variant_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            # Automatically generate slug from name if not provided
            self.sku = generate_sku(prefix="VAMS-B",length=6)
        super().save(*args, **kwargs)


# ---------- MUSICAL INSTRUMENT PRODUCT ----------

class MusicalInstrument(Product):
    sub_category = models.ForeignKey(SubCategory, related_name="musical_instruments", on_delete=models.CASCADE)
    brand = models.CharField(_("Brand"), max_length=255)
    model = models.CharField(max_length=255)
    instrument_type = models.CharField(max_length=100)
    material = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} - {self.sub_category.name}"

    class Meta:
        verbose_name = "Musical Instrument"
        verbose_name_plural = "Musical Instruments"

class MusicalInstrumentVariant(models.Model):
    product = models.ForeignKey(MusicalInstrument, verbose_name=_("Product"), on_delete=models.CASCADE, related_name="variants")
    color = models.CharField(_("Color"), max_length=50, null=True)
    image = models.ImageField(upload_to='variant_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True,null=True,blank=True)
    created_at = models.DateTimeField(_("CreatedAt"), auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(_("ModifiedAt"), auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = _("MusicalInstrumentVariant")
        verbose_name_plural = _("MusicalInstrumentVariants")

    def __str__(self):
        return self.product.name

    def get_absolute_url(self):
        return reverse("MusicalInstrumentVariant_detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
        if not self.sku:
            # Automatically generate slug from name if not provided
            self.sku = generate_sku(prefix="VAMS-MI",length=6)
        super().save(*args, **kwargs)

# ---------- ELECTRONIC PRODUCT ----------

class Electronic(Product):
    sub_category = models.ForeignKey(SubCategory, related_name="electronics", on_delete=models.CASCADE)
    brand = models.CharField(max_length=255,blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    warranty_period = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.sub_category.name}"

class ElectronicsVariant(models.Model):
    product = models.ForeignKey(Electronic, verbose_name=_("Product"), on_delete=models.CASCADE, related_name="variants")
    color = models.CharField(_("Color"), max_length=50, null=True)
    image = models.ImageField(upload_to='variant_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True,null=True,blank=True)
    created_at = models.DateTimeField(_("CreatedAt"), auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(_("ModifiedAt"), auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = _("ElectronicsVariant")
        verbose_name_plural = _("ElectronicsVariants")

    def __str__(self):
        return self.product.name

    def get_absolute_url(self):
        return reverse("ElectronicsVariant_detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
        if not self.sku:
            # Automatically generate slug from name if not provided
            self.sku = generate_sku(prefix="VAMS-EI",length=6)
        super().save(*args, **kwargs)

# ---------- BILLING ADDRESS ----------

class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name}, {self.city}, {self.country}"

    def save(self, *args, **kwargs):
        if self.is_default:
            BillingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Billing Addresses"


# ---------- ORDER ----------

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(BillingAddress, verbose_name=_("Billing Address"), on_delete=models.CASCADE, null=True, blank=True)
    payment_status = models.BooleanField(_("Payment Status"), default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

    def update_total_price(self):
        total = sum(item.get_total_price() for item in self.items.all())
        self.total_price = total
        self.save()

    @property
    def sid(self):
        return f"VAMS/{date.today().strftime('%Y/%m%d')}/{self.id}"

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)
    price_at_order_time = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.price_at_order_time * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"

class Payment(models.Model):
    GATEWAY_CHOICES = [
        ('razorpay', 'RazorPay'),
        ('phonepe', 'PhonePe'),
        ('stripe', 'Stripe'),  # scalable
        ('cash', 'Cash'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES)
    status = models.BooleanField(_("Payment Status"), default=False)

    razorpay_order_id = models.CharField(_("RazorPay Order Id"), max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(_("RazorPay Payment Id"), max_length=500, null=True, blank=True)

    phonepe_id = models.CharField(_("PhonePe Payment Id"), max_length=100, null=True, blank=True)
    phonepe_merchant_transaction_id = models.CharField(_("PhonePe Transaction Id"), max_length=36, null=True, blank=True)

    stripe_charge_id = models.CharField(_("Stripe Charge ID"), max_length=255, null=True, blank=True)

    code = models.CharField(_("Response Code"), max_length=50, blank=True, null=True)
    message = models.TextField(_("Message"), blank=True, null=True)
    redirect_url = models.TextField(_("Redirect URL"), blank=True, null=True)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"{self.gateway} Payment for Order {self.order.id}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")



# ---------- PHONEPE PAYMENT ----------

class PhonePePaymentRequestDetail(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.SET_NULL, blank=True, null=True)
    order_id = models.ForeignKey(Order, verbose_name=_("Order Id"), on_delete=models.CASCADE, blank=True, null=True)
    amount = models.CharField(_("Amount"), max_length=50, null=True, blank=True)
    success = models.BooleanField(_("Success"), default=False)
    code = models.CharField(_("Code"), max_length=50, blank=True, null=True)
    message = models.TextField(_("Message"))
    merchant_transaction_id = models.CharField(_("Merchant Transaction Id"), max_length=200, null=True, blank=True)
    transaction_id = models.CharField(_("Transaction Id"), max_length=200, null=True, blank=True)
    redirect_url = models.TextField(_("URL"))
    created_at = models.DateTimeField(_("Created At"), auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order_id_id if self.order_id else '-'}"

    def get_absolute_url(self):
        return reverse("PhonePePaymentDetail_detail", kwargs={"pk": self.pk})

    def get_order_sid(self):
        return self.order_id.sid

    class Meta:
        verbose_name = _("PhonePe Payment Detail")
        verbose_name_plural = _("PhonePe Payment Details")


# ---------- EARNINGS ----------

class Earning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')

    quantity_sold = models.PositiveIntegerField(default=0)
    total_earning = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.BooleanField(_("Is Payment Released"), default=False)
    modified_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total_earning = Decimal(self.item.price) * Decimal(self.quantity_sold) * Decimal(0.60)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Earnings for {self.user} from {self.item} on {self.modified_at}"


# ---------- UNSUBSCRIBE ----------

class UnsubscribedEmail(models.Model):
    email = models.EmailField(unique=True)
    unsubscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# ---------- LEGAL CONTENT ----------

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
