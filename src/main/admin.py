# store/admin.py

from django.contrib import admin
from .models import Item, ExamCategory, Order

admin.site.register(Item)
admin.site.register(ExamCategory)
admin.site.register(Order)
