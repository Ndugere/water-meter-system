from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.utils import timezone
from .forms import CustomerForm, MeterForm, BillForm, PaymentForm



from .models import Customer, Meter, MeterReading, Bill, Payment, Notification, Tariff


@login_required
def dashboard(request):
    """Main dashboard: show high-level stats"""
    total_customers = Customer.objects.count()
    total_meters = Meter.objects.count()
    unpaid_bills = Bill.objects.filter(is_paid=False).count()

    total_billed = Bill.objects.aggregate(
        total=Coalesce(Sum("amount_due"), Decimal("0.00"))
    )["total"]

    total_due = Bill.objects.filter(is_paid=False).aggregate(
        total=Coalesce(Sum("amount_due"), Decimal("0.00"))
    )["total"]

    total_collected = Payment.objects.aggregate(
        total=Coalesce(Sum("amount"), Decimal("0.00"))
    )["total"]

    readings_today = MeterReading.objects.filter(
        reading_date=timezone.now().date()
    ).count()

    context = {
        "total_customers": total_customers,
        "total_meters": total_meters,
        "unpaid_bills": unpaid_bills,
        "total_billed": total_billed,
        "total_due": total_due,
        "total_collected": total_collected,
        "readings_today": readings_today,
    }
    return render(request, "core/dashboard.html", context)


@login_required
def customers_meters(request):
    """Gateway page for Customers & Meters"""
    return render(request, "core/customers_meters.html")

@login_required
def customers(request):
    """List all customers as clickable cards"""
    all_customers = Customer.objects.all()
    context = {"customers": all_customers}
    return render(request, "core/customers.html", context)

@login_required
def customer_add(request):
    """Add a new customer"""
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customers")
    else:
        form = CustomerForm()

    context = {"form": form}
    return render(request, "core/customer_add.html", context)



@login_required
def customer_detail(request, customer_id):
    """View details for a single customer"""
    customer = Customer.objects.get(id=customer_id)
    context = {"customer": customer}
    return render(request, "core/customer_detail.html", context)

@login_required
def customer_edit(request, id):
    customer = get_object_or_404(Customer, pk=id)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            # Use the correct URL parameter name
            return redirect("customer_detail", customer_id=customer.pk)
    else:
        form = CustomerForm(instance=customer)

    return render(request, "core/customer_edit.html", {
        "form": form,
        "customer": customer,
        "title": "Edit Customer"
    })



@login_required
def customer_delete(request, id):
    customer = get_object_or_404(Customer, id=id)
    
    if request.method == "POST":
        customer.delete()
        return redirect("customers")  # Redirect to customers list
    
    return render(request, "core/customer_confirm_delete.html", {"customer": customer})

@login_required
def meters_list(request):
    """Display all meters"""
    meters = Meter.objects.select_related('customer').all()
    context = {"meters": meters}
    return render(request, "core/meters.html", context)

@login_required
def meter_detail(request, meter_id):
    """Display details of a specific meter and its readings"""
    meter = Meter.objects.select_related('customer').get(id=meter_id)
    readings = meter.readings.all()  # latest readings already ordered by -reading_date
    context = {
        "meter": meter,
        "readings": readings,
    }
    return render(request, "core/meter_detail.html", context)


@login_required
def meter_add(request):
    if request.method == "POST":
        form = MeterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("meters")
    else:
        form = MeterForm()
    return render(request, "core/meter_form.html", {"form": form, "title": "Add Meter"})

@login_required
def meter_edit(request, meter_id):
    meter = get_object_or_404(Meter, pk=meter_id)
    if request.method == "POST":
        form = MeterForm(request.POST, instance=meter)
        if form.is_valid():
            form.save()
            return redirect("meters")
    else:
        form = MeterForm(instance=meter)
    return render(request, "core/meter_form.html", {"form": form, "title": "Edit Meter"})

@login_required
def meter_delete(request, meter_id):
    meter = get_object_or_404(Meter, pk=meter_id)
    if request.method == "POST":
        meter.delete()
        return redirect("meters")
    return render(request, "core/meter_confirm_delete.html", {"meter": meter})


@login_required
def billing_payments(request):
    bills = Bill.objects.select_related('customer', 'reading').all()
    payments = Payment.objects.select_related('bill__customer').all()

    total_billed = bills.aggregate(total=Coalesce(Sum('amount_due'), Decimal('0.00')))['total']
    total_collected = payments.aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
    total_due = total_billed - total_collected
    unpaid_bills_count = bills.filter(is_paid=False).count()

    context = {
        "bills": bills,
        "payments": payments,
        "total_billed": total_billed,
        "total_collected": total_collected,
        "total_due": total_due,
        "unpaid_bills_count": unpaid_bills_count,
    }
    return render(request, "core/billing_payments.html", context)



# ------------------ BILL VIEWS ------------------

@login_required
def bill_add(request):
    if request.method == "POST":
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            # Compute amount due based on meter reading and latest tariff
            bill.amount_due = bill.compute_amount_due()
            bill.save()
            return redirect("billing_payments")  # redirect to bills/payments page
    else:
        form = BillForm()
    return render(request, "core/bill_form.html", {"form": form, "title": "Add Bill"})


@login_required
def bill_edit(request, bill_id):
    bill = get_object_or_404(Bill, pk=bill_id)
    if request.method == "POST":
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.amount_due = bill.compute_amount_due()
            bill.save()
            return redirect("billing_payments")
    else:
        form = BillForm(instance=bill)
    return render(request, "core/bill_form.html", {"form": form, "title": "Edit Bill"})


@login_required
def bill_delete(request, bill_id):
    bill = get_object_or_404(Bill, pk=bill_id)
    if request.method == "POST":
        bill.delete()
        return redirect("billing_payments")
    return render(request, "core/bill_confirm_delete.html", {"bill": bill})


# ------------------ PAYMENT VIEWS ------------------

@login_required
def payment_add(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            # Update related bill status
            payment.bill.update_status()
            return redirect("billing_payments")
    else:
        form = PaymentForm()
    return render(request, "core/payment_form.html", {"form": form, "title": "Add Payment"})


@login_required
def payment_edit(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            payment.bill.update_status()
            return redirect("billing_payments")
    else:
        form = PaymentForm(instance=payment)
    return render(request, "core/payment_form.html", {"form": form, "title": "Edit Payment"})


@login_required
def payment_delete(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    if request.method == "POST":
        bill = payment.bill
        payment.delete()
        bill.update_status()
        return redirect("billing_payments")
    return render(request, "core/payment_confirm_delete.html", {"payment": payment})


# ======================
# CATEGORY VIEWS
# ======================

@login_required
def water_management(request):
    meters = Meter.objects.select_related("customer")
    recent_readings = MeterReading.objects.select_related("meter")[:10]
    customers = Customer.objects.all()

    context = {
        "meters": meters,
        "recent_readings": recent_readings,
        "customers": customers,
    }
    return render(request, "categories/water_management.html", context)




@login_required
def reports_analysis(request):
    total_consumption = MeterReading.objects.aggregate(
        total=Coalesce(Sum("units_consumed"), Decimal("0.00"))
    )["total"]

    revenue = Payment.objects.aggregate(
        total=Coalesce(Sum("amount"), Decimal("0.00"))
    )["total"]

    top_customers = (
        Customer.objects.annotate(total_due=Sum("bills__amount_due"))
        .order_by("-total_due")[:5]
    )

    context = {
        "total_consumption": total_consumption,
        "revenue": revenue,
        "top_customers": top_customers,
    }
    return render(request, "categories/reports_analysis.html", context)


@login_required
def system_settings(request):
    users = Customer.objects.count()
    notifications = Notification.objects.select_related("customer")[:10]
    pending_notifications = notifications.filter(is_sent=False).count()

    context = {
        "users": users,
        "notifications": notifications,
        "pending_notifications": pending_notifications,
    }
    return render(request, "categories/system_settings.html", context)
