# forms.py
from django import forms
from .models import BookVariant, Product

class ProductForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,  
            'cols': 50, 
        })
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'image']

class BookVariantForm(forms.ModelForm):
    class Meta:
        model = BookVariant
        fields = ['pdf_file', 'price', 'sku', 'is_free', 'is_downloadable']


