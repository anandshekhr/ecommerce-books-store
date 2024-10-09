from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(EmailContent)
class EmailContentAdmin(admin.ModelAdmin):
    list_display = ('subject','created_at') 

@admin.register(EmailSendRequestLog)
class EmailSendRequestLogAdmin(admin.ModelAdmin):
    list_display = ('name','start_index','end_index','created_at')

@admin.register(EmailWhatsappTable)
class EmailWhatsappTableAdmin(admin.ModelAdmin):
    list_display = ('name','gender','email','mobile','created_at')

@admin.register(TbEmailSentLog)
class TbEmailSentLogAdmin(admin.ModelAdmin):
    list_display = ('email','mobile','created_at')

    

    

    
