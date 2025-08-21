from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.utils import timezone  # <-- You also forgot this import

from .models import Customer, MeterReading, Bill, Payment, Notification, User


class UserLoginView(LoginView):
    template_name = "core/login.html"


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("login")  # Redirect to login after logout


@login_required
def dashboard(request):
    # Stats
    total_customers = Customer.objects.count()
    active_readers = User.objects.filter(is_active=True).count()
    outstanding_balance = Bill.objects.aggregate(
        total=Coalesce(Sum("amount_due") - Sum("payments__amount"), Decimal("0.00"))
    )["total"] or Decimal("0.00")

    # FIX: handle DateField vs DateTimeField properly
    today = timezone.now().date()
    try:
        readings_today = MeterReading.objects.filter(reading_date__date=today).count()  # If DateTimeField
    except Exception:
        readings_today = MeterReading.objects.filter(reading_date=today).count()  # If DateField

    # Recent data
    recent_readings = (
        MeterReading.objects.select_related("meter__customer")
        .order_by("-reading_date")[:5]
    )
    notifications = Notification.objects.select_related("customer").order_by("-created_at")[:5]

    context = {
        "total_customers": total_customers,
        "active_readers": active_readers,
        "outstanding_balance": outstanding_balance,
        "readings_today": readings_today,
        "recent_readings": recent_readings,
        "notifications": notifications,
    }
    return render(request, "core/dashboard.html", context)
