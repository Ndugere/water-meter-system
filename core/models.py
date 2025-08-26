from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.functions import Coalesce
from decimal import Decimal

# -------------------------
# User Model
# -------------------------
class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


# -------------------------
# Customer Model
# -------------------------
class Customer(models.Model):
    name = models.CharField(max_length=255)
    house_number = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.house_number})"

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


# -------------------------
# Meter Model
# -------------------------
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


# -------------------------
# Tariff Model
# -------------------------
class Tariff(models.Model):
    effective_date = models.DateField(default=timezone.now)
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-effective_date"]

    def __str__(self):
        return f"Tariff {self.rate_per_unit} (from {self.effective_date})"


# -------------------------
# MeterReading Model
# -------------------------
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
        ordering = ["reading_date"]

    def __str__(self):
        return f"Reading {self.value} on {self.reading_date} ({self.meter})"

    def compute_units(self):
        """Compute units consumed since previous reading."""
        previous = self.meter.readings.exclude(pk=self.pk).order_by("-reading_date").first()
        if previous:
            self.units_consumed = max(self.value - previous.value, 0)
        else:
            self.units_consumed = self.value  # first reading
        self.save(update_fields=["units_consumed"])


# -------------------------
# Bill Model
# -------------------------
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
        ordering = ["issue_date"]

    def __str__(self):
        return f"Bill {self.id} - {self.customer.name} - {self.amount_due}"

    @classmethod
    def create_from_reading(cls, reading: MeterReading, due_days: int = 7):
        reading.compute_units()

        latest_tariff = Tariff.objects.order_by("-effective_date").first()
        if not latest_tariff:
            raise ValidationError("No tariff defined.")

        # Base amount
        amount_due = round(reading.units_consumed * latest_tariff.rate_per_unit, 2)

        # Adjust for previous balance
        previous_balance = reading.meter.customer.balance
        amount_due -= previous_balance

        # Set due date
        due_date = timezone.now().date() + timezone.timedelta(days=due_days)

        bill = cls.objects.create(
            customer=reading.meter.customer,
            reading=reading,
            amount_due=amount_due,
            due_date=due_date,
        )
        bill.update_status()
        return bill

    def update_status(self):
        """Automatically update is_paid based on payments and balance."""
        total_paid = self.payments.aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]
        self.is_paid = total_paid >= self.amount_due
        self.save(update_fields=["is_paid"])

    def compute_amount_due(self):
        """Calculate amount due for this reading including previous balance."""
        latest_tariff = Tariff.objects.order_by("-effective_date").first()
        if not latest_tariff:
            raise ValidationError("No tariff defined.")

        base_amount = self.reading.units_consumed * latest_tariff.rate_per_unit
        previous_balance = self.customer.balance
        return round(base_amount - previous_balance, 2)


# -------------------------
# Payment Model
# -------------------------
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


# -------------------------
# Notification Model
# -------------------------
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
