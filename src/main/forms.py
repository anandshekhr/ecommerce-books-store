# forms.py
from django import forms
from .models import BookVariant, Product, Book

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

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'name', 'category', 'sub_category', 'author', 'isbn_10', 'isbn_13', 
            'edition', 'publisher', 'publication_date', 'description', 'price', 
            'stock', 'image'
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class BookVariantForm(forms.ModelForm):
    class Meta:
        model = BookVariant
        fields = ['format', 'price', 'stock', 'is_free', 'is_downloadable', 'pdf_file', 'image']


