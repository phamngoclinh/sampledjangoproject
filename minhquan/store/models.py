from django.db import models
from django.contrib.auth.models import User

from datetime import datetime


class BaseModel(models.Model):
  created_date = models.DateTimeField(default=datetime.now, blank=True)
  updated_date = models.DateTimeField(default=datetime.now, blank=True)
  active = models.BooleanField(default=True)

  def __str__(self):
    return hasattr(self, 'name') and self.name or 'Name is undefined'

  class Meta:
    abstract = True


class Partner(BaseModel):
  user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
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
  category = models.ForeignKey(UOMCategory, on_delete=models.CASCADE)
  name = models.CharField(max_length=200)


class Address(BaseModel):
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
  
  products = models.ManyToManyField('Product')
  name = models.CharField(max_length=200)
  rule_product = models.CharField(max_length=200)
  rule_customer = models.CharField(max_length=200)
  start_date = models.DateTimeField(default=datetime.now)
  expired_date = models.DateTimeField(default=datetime.now)
  discount_type = models.CharField(default='percent', max_length=50, choices=DISCOUNT_TYPE)
  discount = models.FloatField(default=0)

  # @property
  # def products(self):
  #   return Product.objects.raw(f'SELECT * FROM store_product WHERE {self.rule_product}')

  def discount_price(self, price):
    return price * (100.0 - self.discount) / 100.0 if self.discount_type == 'percent' else (price - self.discount  if price - self.discount > 0 else 0)


class Coupon(BaseModel):
  program = models.ForeignKey(CouponProgram, on_delete=models.CASCADE)
  code = models.CharField(max_length=200)
  start_date = models.DateTimeField()
  expired_date = models.DateTimeField()
  pos = models.ForeignKey('POS', on_delete=models.CASCADE, null=True, blank=True)

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
  uom = models.ForeignKey(UOM, on_delete=models.CASCADE)
  category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
  name = models.CharField(max_length=200)
  slug = models.SlugField(unique=True, null=True)
  description = models.CharField(max_length=500)
  image = models.ImageField(max_length=200)
  price = models.FloatField(default=0)
  # Formular: sub_price = CouponProgram.discount_price(Product.price)
  sub_price = models.FloatField(default=0)
  

  # def coupon_programs(self):
  #   coupon_programs = CouponProgram.objects.filter(start_date__lte=datetime.today(), expired_date__gte=datetime.today())
  #   product_coupon_programs = []
  #   for coupon_program in coupon_programs:
  #     for product in coupon_program.products:
  #       if product.id == self.id:
  #         product_coupon_programs.append(coupon_program)
  #   return product_coupon_programs
  
  # def coupon_program(self):
  #   coupon_programs = self.coupon_programs()
  #   return coupon_programs[0] if coupon_programs else []

  # def discount_price(self):
  #   coupon_program = self.coupon_program()
  #   return coupon_program.discount_price(self.price) if coupon_program else 0


# class CouponProgramProduct(BaseModel):
#   product = models.ForeignKey(Product, on_delete=models.CASCADE)
#   coupon_program = models.ForeignKey(CouponProgram, on_delete=models.CASCADE)


class POS(BaseModel):
  POS_STATUS = (
    ('draft', 'Draft'),
    ('processing', 'Processing'),
    ('shipping', 'Shipping'),
    ('done', 'Done')
  )

  customer = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True, blank=True)
  receive_name = models.CharField(max_length=100, null=True, blank=True)
  receive_phone = models.IntegerField(default=0, null=True, blank=True)
  receive_email = models.EmailField(null=False, blank=True)
  # Formular: amount_price = sum(POSDetail.amount_price)
  amount_price = models.FloatField(default=0)
  # Formular: amount_sub_total = sum(POSDetail.sub_total)
  amount_sub_total = models.FloatField(default=0)
  # Formular: amount_discount = CouponProgram.discount_price(POS.amount_sub_total)
  amount_discount = models.FloatField(default=0)
  # Formular: amount_total = POS.amount_sub_total - POS.amount_discount
  amount_total = models.FloatField(default=0) # Include discount amount, tax amount
  # Formular: amount_discount_total = sum(POSDetail.price_discount) + POS.amount_discount
  amount_discount_total = models.FloatField(default=0)
  status = models.CharField(default='draft', max_length=100, choices=POS_STATUS)
  shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
  note = models.CharField(max_length=200, null=True, blank=True)

  def __str__(self):
    return 'DH - %d' % self.id
  
  def calculate(self):
    amount_price = amount_sub_total = amount_discount_total = 0
    for posdetail in self.posdetail_set.all():
      amount_price += posdetail.amount_price
      amount_sub_total += posdetail.sub_total
      amount_discount_total += posdetail.price_discount
    
    # self.amount_discount = amount_discount
    self.amount_price = amount_price
    self.amount_sub_total = amount_sub_total
    self.amount_total = amount_sub_total - self.amount_discount
    self.amount_discount_total = amount_discount_total + self.amount_discount


class POSDetail(BaseModel):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  pos = models.ForeignKey(POS, on_delete=models.CASCADE)
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
    return '%d - %s' % (self.pos.id, self.product.name)

  def calculate(self):
    self.price_discount = self.quantity * (self.price_unit - self.sub_price_unit)
    self.amount_price = self.quantity * self.price_unit
    self.sub_total = self.amount_price - self.price_discount