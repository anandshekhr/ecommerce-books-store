# forms.py
from django import forms
from .models import Item

class ProductForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,  
            'cols': 50, 
        })
    )
    class Meta:
        model = Item
        fields = ['title', 'description','category' ,'thumbnail','pdf_file','price', 'og_price','is_free','is_downloadable']  

    
