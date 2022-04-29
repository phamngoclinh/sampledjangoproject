from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


ORDER_DELIVERY_STATUS_CHOICES = (
  ('pending', 'Chưa giải quyết'), # Customer started the checkout process but did not complete it. Incomplete orders are assigned a "Pending" status and can be found under the More tab in the View Orders screen.
  ('awaiting_payment', 'Đang thanh toán'), # Customer has completed the checkout process, but payment has yet to be confirmed. Authorize only transactions that are not yet captured have this status.
  ('awaiting_fulfillment', 'Thanh toán thành công'), # Customer has completed the checkout process and payment has been confirmed.
  ('awaiting_shipment', 'Chờ shipper nhận hàng'), # Order has been pulled and packaged and is awaiting collection from a shipping provider.
  ('awaiting_pickup', 'Chờ khách hàng nhận hàng'), # Order has been packaged and is awaiting customer pickup from a seller-specified location.
  ('partially_shipped', 'Đã giao hàng một phần'), #  Only some items in the order have been shipped.
  ('shipped', 'Đã giao hàng'), # Order has been shipped, but receipt has not been confirmed; seller has used the Ship Items action. A listing of all orders with a "Shipped" status can be found under the More tab of the View Orders screen.
  ('completed', 'Đã hoàn thành'), # Order has been shipped/picked up, and receipt is confirmed; client has paid for their digital product, and their file(s) are available for download.
  ('cancelled', 'Đã hủy'), # Seller has cancelled an order, due to a stock inconsistency or other reasons. Stock levels will automatically update depending on your Inventory Settings. Cancelling an order will not refund the order. This status is triggered automatically when an order using an authorize-only payment gateway is voided in the control panel before capturing payment.
  ('declined', 'Đã từ chối'), # Seller has marked the order as declined.
  ('partially_refunded', 'Đã hoàn lại một phần'), # Seller has partially refunded the order.
  ('refunded', 'Đã hoàn lại'), # Seller has used the Refund action to refund the whole order. A listing of all orders with a "Refunded" status can be found under the More tab of the View Orders screen.
  ('disputed', 'Đang tranh chấp'), # Customer has initiated a dispute resolution process for the PayPal transaction that paid for the order or the seller has marked the order as a fraudulent order.
)


class BaseModel(models.Model):
  created_date = models.DateTimeField(default=datetime.now, blank=True)
  updated_date = models.DateTimeField(default=datetime.now, blank=True)
  active = models.BooleanField(default=True)

  def __str__(self):
    return hasattr(self, 'name') and self.name or 'Name is undefined'

  class Meta:
    abstract = True


class Partner(BaseModel):
  user = models.OneToOneField(User, related_name='partner', on_delete=models.CASCADE, null=True, blank=True)
  phone = models.IntegerField(unique=True, null=True, blank=True)
  email = models.EmailField(unique=True)
  full_name = models.CharField(null=True, max_length=200, blank=True)
  first_name = models.CharField(null=True, max_length=50, blank=True)
  last_name = models.CharField(null=True, max_length=50, blank=True)
  dob = models.DateTimeField(null=True, blank=True)
  is_customer = models.BooleanField(default=True)
  is_vendor = models.BooleanField(default=False)

  # class Meta:
  #     constraints = [
  #         models.CheckConstraint(
  #             check=Q(phone__isnull=True, email__isnull=False) | Q(phone__isnull=False, email__isnull=True),
  #             name='only_phone_or_email'
  #         )
  #     ]

  def __str__(self):
    return self.email or self.phone or self.full_name or self.first_name

class UOMCategory(BaseModel):
  name = models.CharField(max_length=200, unique=True)


class UOM(BaseModel): # Unit of measure
  category = models.ForeignKey(UOMCategory, related_name='uoms', on_delete=models.CASCADE)
  name = models.CharField(max_length=200)


class Address(BaseModel):
  partner = models.ForeignKey(Partner, related_name='addresses', on_delete=models.CASCADE, null=True, blank=True)
  city = models.CharField(max_length=50)
  district = models.CharField(max_length=50)
  award = models.CharField(max_length=50)
  address = models.CharField(max_length=100)

  def __str__(self):
      return ', '.join([self.address, self.award, self.district, self.city])


class CouponProgram(BaseModel):
  DISCOUNT_TYPE = (
    ('percent', 'Percent'),
    ('fixed', 'Fixed Amount'),
  )
  
  products = models.ManyToManyField('Product', related_name='couponprograms')
  name = models.CharField(max_length=200)
  rule_product = models.JSONField(null=True, blank=True)
  rule_order = models.JSONField(null=True, blank=True)
  rule_customer = models.JSONField(null=True, blank=True)
  start_date = models.DateTimeField(default=datetime.now)
  expired_date = models.DateTimeField(default=datetime.now)
  discount_type = models.CharField(default='percent', max_length=50, choices=DISCOUNT_TYPE)
  discount = models.FloatField(default=0)

  def calcute_discount(self, price):
    return price * self.discount / 100.0 if self.discount_type == 'percent' else (0 if self.discount > price else self.discount)
  
  def is_available(self):
    return self.start_date <= datetime.today() and self.expired_date >= datetime.today()


class Coupon(BaseModel):
  program = models.ForeignKey(CouponProgram, related_name='coupons', on_delete=models.CASCADE)
  order = models.ForeignKey('Order', related_name='coupons', on_delete=models.CASCADE, null=True, blank=True)
  code = models.CharField(max_length=200)
  start_date = models.DateTimeField()
  expired_date = models.DateTimeField()

  def __str__(self):
    return self.code


class ProductCategory(BaseModel):
  parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
  name = models.CharField(max_length=200)
  slug = models.SlugField(unique=True, null=True)

  def get_parents(self):
    p_list = []
    if self.parent_id:
      more = self.parent
      while more:
        p_list.append(more)
        more = more.parent
    return p_list

  def get_childrens(self):
    c_list = []
    more = [self]
    while more:
      ids = [i.id for i in more]
      more = ProductCategory.objects.filter(parent_id__in=ids)
      c_list.extend(more)
    return c_list


class Product(BaseModel):
  uom = models.ForeignKey(UOM, related_name='products', on_delete=models.CASCADE)
  category = models.ForeignKey(ProductCategory, related_name='products', on_delete=models.CASCADE)
  name = models.CharField(max_length=200)
  slug = models.SlugField(unique=True, null=True)
  description = models.CharField(max_length=500)
  image = models.ImageField(max_length=200)
  price = models.FloatField(default=0)

  @property
  def price_discount(self):
    coupon_program = self.get_coupon_program()
    if not coupon_program or not coupon_program.is_available():
      return 0
    return coupon_program.calcute_discount(self.price)

  @property
  def sub_price(self):
    return self.price - self.price_discount

  def get_coupon_program(self):
    return self.couponprograms.first()
  

class Order(BaseModel):
  customer = models.ForeignKey(Partner, related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
  created_user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
  # orderdeliver = models.OneToOneField('OrderDeliver', related_name='order', on_delete=models.CASCADE, null=True)
  shipping_address = models.ForeignKey(Address, related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
  status = models.CharField(default='pending', max_length=100, choices=ORDER_DELIVERY_STATUS_CHOICES)
  receive_name = models.CharField(max_length=100, null=True, blank=True)
  receive_phone = models.IntegerField(default=0, null=True, blank=True)
  receive_email = models.EmailField(null=False, blank=True)
  # Formular: amount_price = sum(OrderDetail.amount_price)
  amount_price = models.FloatField(default=0)
  # Formular: amount_sub_total = sum(OrderDetail.sub_total)
  amount_sub_total = models.FloatField(default=0)
  # Formular: amount_discount = CouponProgram.calcute_discount(Order.amount_sub_total)
  amount_discount = models.FloatField(default=0)
  # Formular: amount_total = Order.amount_sub_total - Order.amount_discount
  amount_total = models.FloatField(default=0) # Include discount amount, tax amount
  # Formular: amount_discount_total = sum(OrderDetail.price_discount) + Order.amount_discount
  amount_discount_total = models.FloatField(default=0)
  note = models.CharField(max_length=200, null=True, blank=True)
  
  def __str__(self):
    return 'DH - %d' % self.id

  @property
  def orderdeliver(self):
    return OrderDeliver.objects.get(order=self, status=self.status)
  
  def compute(self):
    # Sum of orderdetails
    amount_price = amount_sub_total = amount_discount_total = 0
    for orderdetail in self.orderdetails.all():
      amount_price += orderdetail.amount_price
      amount_sub_total += orderdetail.sub_total
      amount_discount_total += orderdetail.price_discount
    
    # Calculate discount on whole order
    if self.coupons:
      amount_discount = 0
      for coupon in self.coupons.all():
        amount_discount += coupon.program.calcute_discount(self.amount_sub_total)
      self.amount_discount = amount_discount
    
    self.amount_price = amount_price
    self.amount_sub_total = amount_sub_total
    self.amount_total = amount_sub_total - self.amount_discount
    self.amount_discount_total = amount_discount_total + self.amount_discount
  
  def update_status(self, new_status, **kwargs):
    orderdeliver, is_new = OrderDeliver.objects.get_or_create(order=self, status=new_status)
    
    is_updated = False
    if 'started_user' in kwargs:
      orderdeliver.started_user = kwargs.get('started_user')
      is_updated = True
    if 'note' in kwargs:
      orderdeliver.note = kwargs.get('note')
      is_updated = True
    if is_updated:
      orderdeliver.save()
      
    self.status = orderdeliver.status
    self.save()
  
  def pending(self, user=None, note=None):
    self.update_status('pending', started_user=user, note=note)
  
  def awaiting_payment(self, user=None, note=None):
    self.update_status('awaiting_payment', started_user=user, note=note)

  def awaiting_fulfillment(self, user, note=None):
    self.update_status('awaiting_fulfillment', started_user=user, note=note)

  def awaiting_shipment(self, user, note=None):
    self.update_status('awaiting_shipment', started_user=user, note=note)
  
  def awaiting_pickup(self, user, note=None):
    self.update_status('awaiting_pickup', started_user=user, note=note)

  def partially_shipped(self, user, note=None):
    self.update_status('partially_shipped', started_user=user, note=note)

  def shipped(self, user, note=None):
    self.update_status('shipped', started_user=user, note=note)

  def completed(self, user, note=None):
    self.update_status('completed', started_user=user, note=note)

  def cancelled(self, user, note=None):
    self.update_status('cancelled', started_user=user, note=note)

  def declined(self, user, note=None):
    self.update_status('declined', started_user=user, note=note)

  def refunded(self, user, note=None):
    self.update_status('refunded', started_user=user, note=note)

  def partially_refunded(self, user, note=None):
    self.update_status('partially_refunded', started_user=user, note=note)
  
  def disputed(self, user, note=None):
    self.update_status('disputed', started_user=user, note=note)

class OrderDeliver(BaseModel):
  order = models.ForeignKey(Order, related_name='orderdelivers', on_delete=models.CASCADE, null=False, blank=True)
  started_user = models.ForeignKey(User, related_name='started_orderdelivers', on_delete=models.CASCADE, null=True, blank=True)
  status = models.CharField(default='pending', max_length=100, choices=ORDER_DELIVERY_STATUS_CHOICES)
  note = models.CharField(max_length=200, null=True, blank=True)

  def __str__(self):
    return f'DH {self.order.id} - {dict(ORDER_DELIVERY_STATUS_CHOICES)[self.status]}'


class OrderDetail(BaseModel):
  product = models.ForeignKey(Product, related_name='orderdetails', on_delete=models.CASCADE)
  order = models.ForeignKey(Order, related_name='orderdetails', on_delete=models.CASCADE)
  quantity = models.FloatField(default=1)
  price_unit = models.FloatField(default=0)
  sub_price_unit = models.FloatField(default=0)
  # (Số tiền được chiết khấu) price_discount = (price_unit - sub_price_unit) * quantity
  price_discount = models.FloatField(default=0)
  # amount_price = price_unit * quantity
  amount_price = models.FloatField(default=0) # Exclude discount, exclude tax
  # sub_total = amount_price - price_discount
  sub_total = models.FloatField(default=0) # Include discount, exclude tax

  def __str__(self):
    return 'DH %d - Product %s' % (self.order.id, self.product.name)

  def compute(self):
    self.price_discount = self.quantity * (self.price_unit - self.sub_price_unit)
    self.amount_price = self.quantity * self.price_unit
    self.sub_total = self.amount_price - self.price_discount