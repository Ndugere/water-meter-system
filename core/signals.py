from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MeterReading, Bill, Payment


@receiver(post_save, sender=MeterReading)
def create_or_update_bill_from_reading(sender, instance, created, **kwargs):
    """When a reading is saved, calculate units consumed and create/update bill."""
    if created:
        # Calculate consumption
        previous_reading = (
            instance.meter.readings.exclude(id=instance.id)
            .order_by("-reading_date")
            .first()
        )
        if previous_reading:
            instance.units_consumed = max(
                instance.value - previous_reading.value, 0
            )
        else:
            instance.units_consumed = instance.value
        instance.save(update_fields=["units_consumed"])

        # Create bill
        due_date = instance.reading_date.replace(
            day=min(instance.reading_date.day + 14, 28)
        )
        bill = Bill.objects.create(
            customer=instance.meter.customer,
            reading=instance,
            due_date=due_date,
        )
        bill.amount_due = bill.compute_amount_due()
        bill.save(update_fields=["amount_due"])


@receiver(post_save, sender=Payment)
def update_bill_status(sender, instance, created, **kwargs):
    """Update bill payment status after every payment."""
    if created:
        instance.bill.update_status()
