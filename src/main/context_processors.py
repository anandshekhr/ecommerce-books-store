# core/context_processors.py

from .models import Category, SubCategory  # or any model you want to inject

def global_vars(request):
    books_subcategory = SubCategory.objects.filter(parent_category__name='Books')
    mi_subcategory = SubCategory.objects.filter(parent_category__name='Musical Instruments')
    ele_subcategory = SubCategory.objects.filter(parent_category__name='Electronics')
    return {
        'SITE_NAME': 'VAMS BookStore',
        'CONTACT_EMAIL': 'support@vamsbookstore.in',
        'categories': Category.objects.all(),  # e.g., for navbar dropdown
        'books_subcategories':books_subcategory,
        'mi_subcategories':mi_subcategory,
        'ele_subcategories':ele_subcategory
    }
