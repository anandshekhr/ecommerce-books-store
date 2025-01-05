from django.contrib import admin
from .models import *

@admin.register(RequestDataLog)
class RequestDataLogAdmin(admin.ModelAdmin):
    list_display = ('method','path','mobile','is_new_user','country','timestamp')
    

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('error_message','timestamp')
    

