from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','phone_number','occupation','bank_name','bank_account_no','ifsc_code','created_at')
    

