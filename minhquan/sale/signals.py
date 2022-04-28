from datetime import datetime
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Order, OrderDeliver, OrderDetail

@receiver(pre_save, sender=Order)
def compute_order(sender, instance, raw, using, update_fields, **kwargs):
  current_object = instance
  current_object.compute()

@receiver(pre_save, sender=OrderDetail)
def compute_orderdetail(sender, instance, raw, using, update_fields, **kwargs):
  current_object = instance
  current_object.compute()

@receiver(post_save, sender=Order)
def create_order_deliver(sender, instance, created, raw, using, update_fields, **kwargs):
  if created:
    OrderDeliver.objects.create(order=instance, status=instance.status)