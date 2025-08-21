from django import forms
from .models import Meter, Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "house_number", "address", "phone_number"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"}),
            "house_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "House Number"}),
            "address": forms.Textarea(attrs={"class": "form-control", "placeholder": "Customer Address", "rows": 3}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
        }



class MeterForm(forms.ModelForm):
    class Meta:
        model = Meter
        fields = ["customer", "serial_number", "installation_date"]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-select"}),
            "serial_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Meter Serial Number"}),
            "installation_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }