from datetime import datetime
import json

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import inlineformset_factory, modelformset_factory

from minhquan.widgets import SearchInputWidget

from .models import Address, Coupon, CouponProgram, Order, OrderDetail, Partner


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


class CouponProgramModelForm(forms.ModelForm):
  class Meta:
    model = CouponProgram
    fields = '__all__'
    exclude = ['products']
    labels = {
      'products': 'Sản phẩm áp dụng',
      'name': 'Tên CT',
      'rule_product': 'Cài đặt sản phẩm',
      'rule_order': 'Cài đặt đơn hàng',
      'rule_customer': 'Cài đặt khách hàng',
      'start_date': 'Ngày bắt đầu',
      'expired_date': 'Ngày kết thúc',
      'reward_type': 'Hình thức áp dụng',
      'discount_type': 'Loại chiết khấu',
      'discount': 'Giá trị chiết khấu',
      'discount_apply_on_type': 'Áp dụng cho',
      'discount_max_amount': 'Chiết khấu tối đa',
      'free_product': 'Sản phẩm',
      'free_product_total': 'Số lượng',
    }
    widgets = {
      'rule_product': forms.HiddenInput(),
      'rule_customer': forms.HiddenInput(),
      'start_date': forms.widgets.DateInput(attrs={'type': 'date'}),
      'expired_date': forms.widgets.DateInput(attrs={'type': 'date'}),
    }

class CouponModelForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.fields['code'].widget.attrs['readonly'] = True
    # self.fields['start_date'].widget.attrs['readonly'] = True
    # self.fields['expired_date'].widget.attrs['readonly'] = True

  class Meta:
    model = Coupon
    fields = '__all__'
    exclude = ['created_date', 'updated_date', 'active',]
    labels = {
      'code': 'Mã',
      'start_date': 'Ngày hiệu lực',
      'expired_date': 'Ngày hết hạn',
    }
    widgets = {
      'order': forms.HiddenInput(),
      'customer': forms.HiddenInput(),
      'program': forms.HiddenInput(),
      'start_date': forms.widgets.DateInput(attrs={'type': 'date'}),
      'expired_date': forms.widgets.DateInput(attrs={'type': 'date'}),
    }

CouponInlineFormSet = inlineformset_factory(
  CouponProgram,
  Coupon,
  form=CouponModelForm,
  fields='__all__',
  extra=0,
  can_delete=True,
  can_order=False,
)


class GenerateCouponForm(forms.Form):
  generation_type = forms.ChoiceField(choices=(('num_of_coupon', 'Number of coupon'), ('num_of_selected_customer', 'Number of selected customer')))
  total_coupon = forms.IntegerField(required=False)
  customer = forms.CharField(max_length=500, required=False)


class AddressModelForm(forms.ModelForm):
  class Meta:
    model = Address
    fields = '__all__'
    exclude = ['created_date', 'updated_date', 'active',]
    labels = {
      'partner': 'KH thành viên',
      'city': 'Tỉnh/thành phố',
      'district': 'Quận/huyện',
      'award': 'Phường/thị xã',
      'address': 'Số nhà, đường',
    }
    widgets = {
      'partner': SearchInputWidget(attrs={
        'search_url': '/sale/api/search-customer/',
        'search_fields': 'full_name,email,phone',
        'placeholder': 'Tìm KH thành viên',
      }),
    }

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
    widgets = {
      'customer': SearchInputWidget(attrs={
        'search_url': '/sale/api/search-customer/',
        'search_fields': 'full_name,email,phone',
        'add_form': {
          'form': RegisterForm(),
          'action': '/sale/api/create-partner/'
        },
        'placeholder': 'Nhập tên khách hàng',
      }),
      'shipping_address': SearchInputWidget(attrs={
        'search_url': '/sale/api/search-shipping_address/',
        'search_fields': 'city,district,award,address',
        'related_data': 'customer',
        'add_form': {
          'form': AddressModelForm(),
          'action': '/sale/api/create-address/'
        },
        'placeholder': 'Địa chỉ của khách hàng',
      }),
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
  can_order=False,
  widgets = {
    'product': SearchInputWidget(attrs={
      'search_url': '/sale/api/search-product/',
      'placeholder': 'Nhập tên sản phẩm',
    }),
  }
)

