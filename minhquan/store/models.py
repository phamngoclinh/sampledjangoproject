from django.db import models
from django.contrib.auth.models import User

from datetime import datetime


class BaseModel(models.Model):
  created_date = models.DateTimeField(default=datetime.now, blank=True)
  updated_date = models.DateTimeField(default=datetime.now, blank=True)
  active = models.BooleanField(default=False)

  def __str__(self):
    return hasattr(self, 'name') and self.name or 'Name is undefined'

  class Meta:
    abstract = True


class Partner(BaseModel):
  user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
  phone = models.IntegerField(unique=True)
  email = models.EmailField()
  full_name = models.CharField(max_length=200)
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  dob = models.DateTimeField()


class UOMCategory(BaseModel):
  name = models.CharField(max_length=200, unique=True)


class UOM(BaseModel): # Unit of measure
  category = models.ForeignKey(UOMCategory, on_delete=models.CASCADE)
  name = models.CharField(max_length=200)


class CouponProgram(BaseModel):
  DISCOUNT_TYPE = (
    ('percent', 'Percent'),
    ('fixed', 'Fixed Amount'),
  )
  
  name = models.CharField(max_length=200)
  rule_product = models.CharField(max_length=200)
  rule_customer = models.CharField(max_length=200)
  start_date = models.DateTimeField(default=datetime.now)
  expired_date = models.DateTimeField(default=datetime.now)
  discount_type = models.CharField(default='percent', max_length=50, choices=DISCOUNT_TYPE)
  discount = models.FloatField(default=0)

  @property
  def products(self):
    return Product.objects.raw(f'SELECT * FROM store_product WHERE {self.rule_product}')
  
  def discount_price(self, price):
    return price * (100.0 - self.discount) / 100.0 if self.discount_type == 'percent' else (price - self.discount  if price - self.discount > 0 else 0)


class Coupon(BaseModel):
  program = models.ForeignKey(CouponProgram, on_delete=models.CASCADE)
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
  uom = models.ForeignKey(UOM, on_delete=models.CASCADE)
  category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
  name = models.CharField(max_length=200)
  slug = models.SlugField(unique=True, null=True)
  description = models.CharField(max_length=500)
  image = models.ImageField(max_length=200)
  price = models.FloatField(default=0)
  cost = models.FloatField(default=0) # Gia mua


class POS(BaseModel):
  customer = models.CharField(max_length=200)
  total = models.FloatField(default=0)


class POSDetail(BaseModel):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  pos = models.ForeignKey(POS, on_delete=models.CASCADE)
  quantity = models.FloatField(default=0)
  price = models.FloatField(default=0)
  discount = models.FloatField(default=0)
  sub_total = models.FloatField(default=0)
  
