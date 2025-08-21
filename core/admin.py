from django.contrib import admin
from .models import Customer, Meter, MeterReading, Tariff, Bill, Payment, Notification


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "account_number", "phone_number", "balance")
    search_fields = ("name", "account_number")


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "customer", "installation_date")
    search_fields = ("serial_number",)


@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ("meter", "reading_date", "value", "units_consumed")
    list_filter = ("reading_date",)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("rate_per_unit", "effective_date")
    ordering = ("-effective_date",)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("customer", "issue_date", "amount_due", "is_paid", "due_date")
    list_filter = ("is_paid", "issue_date")
    search_fields = ("customer__name", "customer__account_number")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("bill", "amount", "payment_date", "reference_number")
    search_fields = ("reference_number",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("customer", "message", "created_at", "is_sent")
    list_filter = ("is_sent",)
