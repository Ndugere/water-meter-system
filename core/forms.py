from django import forms
from .models import Meter, Customer, Bill, Payment, MeterReading

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
            "customer": forms.Select(attrs={"class": "form-select"}),
            "reading": forms.Select(attrs={"class": "form-select"}),
            "issue_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].empty_label = "Select Customer"
        self.fields["reading"].empty_label = "Select Meter Reading"



class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["bill", "amount", "payment_date", "reference_number"]
        widgets = {
            "bill": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Enter Amount Paid"}),
            "payment_date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "reference_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Payment Reference Number"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bill"].empty_label = "Select Bill"


        
class MeterReadingForm(forms.ModelForm):
    class Meta:
        model = MeterReading
        fields = ["meter", "reading_date", "value"]  # exclude units_consumed
        widgets = {
            "meter": forms.Select(
                attrs={"class": "form-select"}
            ),
            "reading_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "placeholder": "Choose the date"}
            ),
            "value": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter the reading value"}
            ),
        }
        labels = {
            "meter": "Choose the owner of the meter",
            "reading_date": "Reading Date",
            "value": "Reading Value",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change the default "------" option for the Select field
        self.fields["meter"].empty_label = "Select the meter owner"