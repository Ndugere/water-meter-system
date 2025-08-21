from django import forms
from .models import Meter, Customer, Bill, Payment

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


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ["customer", "reading", "issue_date", "due_date"]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-select", "placeholder": "Select Customer"}),
            "reading": forms.Select(attrs={"class": "form-select", "placeholder": "Select Meter Reading"}),
            "issue_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "placeholder": "Select Issue Date"}
            ),
            "due_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "placeholder": "Select Due Date"}
            ),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["bill", "amount", "payment_date", "reference_number"]
        widgets = {
            "bill": forms.Select(attrs={"class": "form-select", "placeholder": "Select Bill"}),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "Enter Amount Paid"}
            ),
            "payment_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                    "placeholder": "Select Payment Date & Time",
                }
            ),
            "reference_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Payment Reference Number"}
            ),
        }
