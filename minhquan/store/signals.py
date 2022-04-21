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
  current_object = instance
  if created:
    current_object.orderdeliver = OrderDeliver.objects.create(order=current_object, started_date=datetime.today())
    OrderDeliver.objects.create(order=current_object, status='confirmed')
    OrderDeliver.objects.create(order=current_object, status='processing')
    OrderDeliver.objects.create(order=current_object, status='shipping')
    OrderDeliver.objects.create(order=current_object, status='done')
    current_object.save()