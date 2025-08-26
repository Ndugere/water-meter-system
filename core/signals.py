from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MeterReading, Bill, Payment, Tariff

# 1️⃣ Auto-create or update Bill when a MeterReading is saved
@receiver(post_save, sender=MeterReading)
def auto_create_or_update_bill(sender, instance, created, **kwargs):
    if created or not hasattr(instance, "bill"):
        Bill.create_from_reading(instance)
    else:
        # Recompute units and update existing bill if reading changes
        instance.compute_units()
        bill = instance.bill
        bill.amount_due = bill.compute_amount_due()
        bill.update_status()
        bill.save()


# 2️⃣ Auto-update Bill status when a Payment is made or updated
@receiver(post_save, sender=Payment)
def auto_update_bill_status(sender, instance, **kwargs):
    instance.bill.update_status()


# 3️⃣ Auto-update Bill status when a Payment is deleted
@receiver(post_delete, sender=Payment)
def auto_update_bill_status_on_delete(sender, instance, **kwargs):
    instance.bill.update_status()


# 4️⃣ Auto-delete related Bill when a MeterReading is deleted
@receiver(post_delete, sender=MeterReading)
def auto_delete_related_bill(sender, instance, **kwargs):
    try:
        instance.bill.delete()
    except Bill.DoesNotExist:
        pass


# 5️⃣ Auto-update all unpaid bills if a new Tariff is added
@receiver(post_save, sender=Tariff)
def auto_update_unpaid_bills_on_tariff_change(sender, instance, **kwargs):
    for bill in Bill.objects.filter(is_paid=False):
        bill.amount_due = bill.compute_amount_due()
        bill.update_status()
        bill.save()
