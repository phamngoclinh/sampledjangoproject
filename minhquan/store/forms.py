from datetime import datetime
import json

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from .models import Coupon, Partner


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
        Coupon.objects.get(code=code, pos__isnull=True, expired_date__gte=datetime.today(), start_date__lte=datetime.today())
    except Coupon.DoesNotExist:
      raise ValidationError('Coupon Code không tồn tại hoặc đã được sử dụng.')
    return code
