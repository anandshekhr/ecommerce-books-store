# store/admin.py

from django.contrib import admin
from .models import *

@admin.register(Book)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id','name','price','stock')
    search_fields = ('id','name','price')
    sortable_by = ('id','name','price')

@admin.register(BookVariant)
class BookVariantAdmin(admin.ModelAdmin):
    list_display = ('product','format','pdf_file')
    
 
@admin.register(Electronic)
class ElectronicAdmin(admin.ModelAdmin):
    list_display = ('id','name','price') 

@admin.register(ElectronicsVariant)
class ElectronicsVariantAdmin(admin.ModelAdmin):
    pass
    


# Musical instrument category and subcategory

@admin.register(MusicalInstrument)
class ProductMusicalInstrumentAdmin(admin.ModelAdmin): 
    pass

@admin.register(MusicalInstrumentVariant)
class MusicalInstrumentVariantAdmin(admin.ModelAdmin):
    pass
    


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product','content_type','image')
    


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    pass  

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user','total_price','created_at')
    search_fields = ('id','user','total_price','created_at')
    sortable_by = ('id','user','total_price','created_at')
    
@admin.register(LegalContent)
class LegalContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_type')
    search_fields = ('title',)

@admin.register(PhonePePaymentRequestDetail)
class PhonePePaymentRequestDetailAdmin(admin.ModelAdmin):
    pass

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id','is_active','user','created_at','updated_at')
    search_fields = ('id','is_active','user','created_at','updated_at')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id','is_active','user','question','created_at','updated_at')
    search_fields = ('id','is_active','user','question','created_at','updated_at')

@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    pass
    


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass



# User Related 
@admin.register(BillingAddress)
class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ('user','full_name','is_default','updated_at')
    

    

