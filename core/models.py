from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.functions import Coalesce
from decimal import Decimal

class User(AbstractUser):
    # Add extra fields if needed (optional)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


class Customer(models.Model):
    name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.account_number})"

    @property
    def balance(self):
        """Outstanding balance (positive = owes, negative = overpaid)."""
        total_billed = self.bills.aggregate(
            total=Coalesce(Sum("amount_due"), Decimal("0.00"))
        )["total"]
        total_paid = self.bills.aggregate(
            total=Coalesce(Sum("payments__amount"), Decimal("0.00"))
        )["total"]
        return round(total_billed - total_paid, 2)


class Meter(models.Model):
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="meter"
    )
    serial_number = models.CharField(max_length=100, unique=True)
    installation_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["serial_number"]

    def __str__(self):
        return f"Meter {self.serial_number} - {self.customer.name}"


class MeterReading(models.Model):
    meter = models.ForeignKey(
        Meter, on_delete=models.CASCADE, related_name="readings"
    )
    reading_date = models.DateField(default=timezone.now)
    value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    units_consumed = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        unique_together = ("meter", "reading_date")
        ordering = ["-reading_date"]

    def __str__(self):
        return f"Reading {self.value} on {self.reading_date} ({self.meter})"


class Tariff(models.Model):
    effective_date = models.DateField(default=timezone.now)
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-effective_date"]

    def __str__(self):
        return f"Tariff {self.rate_per_unit} (from {self.effective_date})"


class Bill(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="bills"
    )
    reading = models.OneToOneField(
        MeterReading, on_delete=models.CASCADE, related_name="bill"
    )
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-issue_date"]

    def __str__(self):
        return f"Bill {self.id} - {self.customer.name} - {self.amount_due}"

    def compute_amount_due(self):
        """Recalculate bill amount based on latest tariff."""
        if not self.reading.units_consumed:
            return Decimal("0.00")
        latest_tariff = Tariff.objects.order_by("-effective_date").first()
        if not latest_tariff:
            raise ValidationError("No tariff defined.")
        return round(self.reading.units_consumed * latest_tariff.rate_per_unit, 2)

    def update_status(self):
        total_paid = self.payments.aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]
        self.is_paid = total_paid >= self.amount_due
        self.save(update_fields=["is_paid"])


class Payment(models.Model):
    bill = models.ForeignKey(
        Bill, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    payment_date = models.DateTimeField(default=timezone.now)
    reference_number = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Payment {self.amount} for {self.bill} on {self.payment_date}"


class Notification(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.customer.name} - {'Sent' if self.is_sent else 'Pending'}"
