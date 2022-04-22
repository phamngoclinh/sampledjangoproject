from datetime import datetime
import json
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.admin import (
    widgets,
    site as admin_site
    )

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.forms import widgets
from django.conf import settings

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import inlineformset_factory, modelformset_factory

from .models import Address, Coupon, Order, OrderDetail, Partner


class ProfileForm(forms.ModelForm):
  phone = models.IntegerField(null=False, blank=False)

  class Meta:
    model = Partner
    fields = ['email', 'phone', 'full_name', 'first_name', 'last_name', 'dob']
    exclude = ['user_id', 'is_vendor', 'is_customer', 'active']
    labels = {
      'phone': 'Điện thoại',
      'full_name': 'Họ & tên',
      'first_name': 'Họ',
      'last_name': 'Tên',
      'dob': 'Năm sinh'
    }
    widgets = {
      'dob': forms.widgets.DateInput(attrs={'type': 'date'})
    }


class LoginForm(forms.Form):
  email = forms.EmailField(max_length=200)
  shopping_cart = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'shopping-cart-data'}), required=False)

  def clean_email(self):
    email = self.cleaned_data['email']
    try:
      Partner.objects.get(email=email)
    except Partner.DoesNotExist:
      raise ValidationError('Email chưa được đăng ký')
    return email
  
  def clean_shopping_cart(self):
    jdata = self.cleaned_data['shopping_cart']
    try:
      json_data = json.loads(jdata)
    except:
      raise ValidationError("Dữ liệu CART_DATA phải là dạng JSON")
    return json_data


class LoginUserForm(forms.Form):
  email = forms.EmailField(max_length=200, widget=forms.HiddenInput())

  def clean_email(self):
    email = self.cleaned_data['email']
    try:
      User.objects.get(email=email)
    except User.DoesNotExist:
      raise ValidationError(f'Email {email} không tồn tại trong hệ thống')
    return email


class LoginOtpForm(forms.Form):
  otp_code = forms.CharField(max_length=8)


class RegisterForm(forms.Form):
  email = forms.EmailField(max_length=200)
  phone = forms.IntegerField(label='Điện thoại')

  def clean_email(self):
    email = self.cleaned_data['email']
    try:
      Partner.objects.get(email=email)
      raise ValidationError('Email đã được đăng ký')
    except Partner.DoesNotExist:
      pass
    return email
  
  def clean_phone(self):
    phone = self.cleaned_data['phone']
    try:
      Partner.objects.get(phone=phone)
      raise ValidationError('Số điện thoại đã được đăng ký')
    except Partner.DoesNotExist:
      pass
    return phone


class ShippingForm(forms.Form):
  address_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'address-id'}), required=False)
  receive_name = forms.CharField(max_length=100, label='Người nhận hàng')
  receive_phone = forms.IntegerField(label='Số điện thoại')
  city = forms.CharField(max_length=50, label='Tỉnh/thành phố')
  district = forms.CharField(max_length=50, label='Quận/huyện')
  award = forms.CharField(max_length=50, label='Phường/thị xã')
  address = forms.CharField(max_length=100, label='Số nhà, đường')
  receive_email = forms.EmailField(label='Địa chỉ email', required=False)
  note = forms.CharField(max_length=200, label='Lưu ý cho người giao hàng', required=False)


class CouponForm(forms.Form):
  code = forms.CharField(max_length=100, required=False)
  coupon_program_id = forms.CharField(widget=forms.HiddenInput(), max_length=10, required=False)

  # check coupon
  def clean_code(self):
    code = self.cleaned_data['code']
    try:
      if code:
        Coupon.objects.get(code=code, order__isnull=True, expired_date__gte=datetime.today(), start_date__lte=datetime.today())
    except Coupon.DoesNotExist:
      raise ValidationError('Coupon Code không tồn tại hoặc đã được sử dụng.')
    return code


AddressFormSet = modelformset_factory(
  Address,
  fields = ['city', 'district', 'award', 'address'],
  labels = {
    'city': 'Tỉnh/thành phố',
    'district': 'Quận/huyện',
    'award': 'Xã/phường',
    'address': 'Số nhà, đường',
    'DELETE':'Xoas'
  },
  error_messages = {
    'city': {
      'max_length': 'Tên tỉnh/thành phố quá dài',
    },
  },
  can_delete=True,
)


class OrderModelForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
  
    self.fields['customer'].widget = (
      RelatedFieldWidgetWrapper( 
        self.fields['customer'].widget,
        self.instance._meta.get_field('customer').remote_field,            
        admin_site,
      )
    )
    self.fields['shipping_address'].widget = (
      RelatedFieldWidgetWrapper( 
        self.fields['shipping_address'].widget,
        self.instance._meta.get_field('shipping_address').remote_field,            
        admin_site,
      )
    )

    self.fields['amount_price'].widget.attrs['readonly'] = True
    self.fields['amount_sub_total'].widget.attrs['readonly'] = True
    self.fields['amount_discount'].widget.attrs['readonly'] = True
    self.fields['amount_discount_total'].widget.attrs['readonly'] = True
    self.fields['amount_total'].widget.attrs['readonly'] = True
    
  class Meta:
    model = Order
    fields = ['customer', 'shipping_address', 'receive_name', 'receive_phone', 'receive_email', 'amount_price', 'amount_sub_total', 'amount_discount', 'amount_discount_total', 'amount_total', 'note',]
    exclude = ['created_date', 'updated_date', 'active', 'orderdeliver', 'created_user',]
    labels = {
      'customer': 'Khách hàng',
      'receive_name': 'Tên người nhận hàng',
      'receive_phone': 'Số điện thoại nhận hàng',
      'receive_email': 'Email nhận hàng',
      'amount_price': 'Tiền chiết khấu',
      'amount_sub_total': 'Thành tiền',
      'amount_discount': 'Chiết khấu trên đơn hàng',
      'amount_total': 'Tổng tiền thanh toán',
      'amount_discount_total': 'Tổng tiền chiết khấu',
      'shipping_address': 'Địa chỉ giao hàng',
      'note': 'Ghi chú của khách hàng',
    }


class OrderDetailModelForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.fields['price_unit'].widget.attrs['readonly'] = True
    self.fields['sub_price_unit'].widget.attrs['readonly'] = True
    self.fields['price_discount'].widget.attrs['readonly'] = True
    self.fields['amount_price'].widget.attrs['readonly'] = True
    self.fields['sub_total'].widget.attrs['readonly'] = True

  class Meta:
    model = OrderDetail
    fields = '__all__'
    exclude = ['created_date', 'updated_date', 'active',]
    labels = {
      'product': 'Sản phẩm',
      'quantity': 'Số lượng',
      'price_unit': 'Đơn giá',
      'sub_price_unit': 'Giá bán',
      'price_discount': 'Tiền chiết khấu',
      'amount_price': 'Thành tiền',
      'sub_total': 'Tổng tiền',
      'note': 'Ghi chú của khách hàng',
    }


OrderDetailInlineFormSet = inlineformset_factory(
  Order,
  OrderDetail,
  form=OrderDetailModelForm,
  fields='__all__',
  extra=0,
  can_delete=True,
  can_order=False
)

