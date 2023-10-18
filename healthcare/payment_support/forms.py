from django import forms
from .models import Purchase


class ProductForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["buyer_name", "email"]
		
    buyer_name = forms.CharField(max_length=100)
    email = forms.EmailField()
