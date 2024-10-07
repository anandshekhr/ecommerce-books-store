from django.contrib import admin
from .models import NewsTheHindu


# Register your models here.
@admin.register(NewsTheHindu)
class NewsTheHinduAdmin(admin.ModelAdmin):
    pass
    
