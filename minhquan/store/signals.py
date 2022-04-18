from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order, OrderDetail

@receiver(pre_save, sender=Order)
def compute_order(sender, instance, raw, using, update_fields, **kwargs):
  current_object = instance
  current_object.compute()

@receiver(pre_save, sender=OrderDetail)
def compute_orderdetail(sender, instance, raw, using, update_fields, **kwargs):
  current_object = instance
  current_object.compute()