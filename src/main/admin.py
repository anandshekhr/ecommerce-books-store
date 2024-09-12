# store/admin.py

from django.contrib import admin
from .models import Item, ExamCategory, Order, LegalContent,PhonePePaymentRequestDetail, ProductImage

admin.site.register(Item)
admin.site.register(ExamCategory)
admin.site.register(Order)
admin.site.register(ProductImage)


@admin.register(LegalContent)
class LegalContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_type')
    search_fields = ('title',)

@admin.register(PhonePePaymentRequestDetail)
class PhonePePaymentRequestDetailAdmin(admin.ModelAdmin):
    pass
    

