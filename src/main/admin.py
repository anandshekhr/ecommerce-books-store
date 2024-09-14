# store/admin.py

from django.contrib import admin
from .models import Item, ExamCategory, Order, LegalContent,PhonePePaymentRequestDetail, ProductImage, Question, Answer

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id','title','price','pdf_file','is_available')
    search_fields = ('id','title','price')
    sortable_by = ('id','title','price')    

@admin.register(ExamCategory)
class ExamCategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name','board')
    search_fields = ('id','name','board')
    sortable_by = ('id','name','board')
    
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id','product','image')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user','total_price','payment_status','created_at')
    search_fields = ('id','user','total_price','payment_status','created_at')
    sortable_by = ('id','user','total_price','payment_status','created_at')
    
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
    

    

    

