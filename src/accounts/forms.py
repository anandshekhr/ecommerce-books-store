from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    billing_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,  
            'cols': 50, 
        })
    )
    class Meta:
        model = UserProfile
        fields = ['occupation', 'company_name', 'phone_number', 'bank_account_no', 'bank_name', 'ifsc_code', 'billing_address']

    def __init__(self, *args, **kwargs):
        editable = kwargs.pop('editable', True)  # Add 'editable' flag
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # If not editable, set fields to readonly/disabled
        if not editable:
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.widget.attrs['disabled'] = True
        
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     for field_name, field in self.fields.items():
    #         if not isinstance(field.widget, forms.CheckboxInput):
    #             field.widget.attrs['class'] = 'form-control'
    
