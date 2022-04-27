from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, reverse
from django.template.response import TemplateResponse

from .decorators import partners_only


from sale import services, forms

def index(request):
  context = {
    'title': 'Trang chủ',
    'group_products': services.get_group_products()
  }
  return TemplateResponse(request, 'store/index.html', context)

def product_category(request, slug):
  group_products = services.get_group_products(slug)
  context = {
    'group_products': group_products,
    'title': 'Danh mục ' + group_products[0]['category'].name
  }
  return TemplateResponse(request, 'store/product_category.html', context)

def product_detail(request, slug):
  product = services.get_product_by_slug(slug)
  context = {
    'product': product,
    'title': product.name
  }
  return TemplateResponse(request, 'store/product_detail.html', context)

def search(request):
  search_text = request.GET.get('tu-khoa', '')
  context = {
    'products': services.search_product(search_text),
    'title': 'Tìm kiếm từ khóa ' + search_text
  }
  return TemplateResponse(request, 'store/search.html', context)

def shopping_cart(request):
  return TemplateResponse(request, 'store/shopping-cart.html', { 'title': 'Giỏ hàng' })

@partners_only
def orders(request):
  context = {
    'orders': services.get_none_draft_orders(customer=request.partner).order_by('-created_date'),
    'title': 'Quản lý đơn hàng'
  }
  return TemplateResponse(request, 'store/orders.html', context)

@partners_only
def order(request, order_id):
  context = { 'title': 'Đơn hàng' }
  order = services.get_partner_order_by_id(order_id, request.partner)
  context['order'] = order
  if order:
    context['deliveries'] = services.get_order_delivers_by_order(order)
    context['title'] = f'Đơn hàng {order.id}'
  return TemplateResponse(request, 'store/order.html', context)

@partners_only
def checkout(request, order_id):
  order = services.get_draft_order(pk=order_id)
  
  if not order or (order.customer != request.partner):
    return redirect('checkout_result', order_id=order_id)
  
  shipping_addresses = services.get_address_by_customer(request.partner)
  context = {
    # 'coupon_programs': services.get_available_coupon_programs(),
    'shipping_addresses': shipping_addresses,
    'title': 'Thanh toán',
  }

  shipping = {
    'city': order.shipping_address and order.shipping_address.city or (shipping_addresses and shipping_addresses.first().city),
    'district': order.shipping_address and order.shipping_address.district or (shipping_addresses and shipping_addresses.first().district),
    'award': order.shipping_address and order.shipping_address.award or (shipping_addresses and shipping_addresses.first().award),
    'address': order.shipping_address and order.shipping_address.address or (shipping_addresses and shipping_addresses.first().address),
    'receive_name': order.receive_name or order.customer.full_name or order.customer.first_name or order.customer.last_name,
    'receive_phone': order.receive_phone or order.customer.phone,
    'receive_email': order.receive_email or order.customer.email,
    'note': order.note or '',
  }
  shipping_form = forms.ShippingForm(shipping)

  coupon = services.get_coupon_by_order(order)
  if coupon:
    coupon_form = forms.CouponForm({ 'code': coupon.code, 'coupon_program_id': coupon.program.id })
  else:
    coupon_form = forms.CouponForm()

  if request.method == 'POST':
    shipping_form = forms.ShippingForm(request.POST)
    coupon_form = forms.CouponForm(request.POST)
    if shipping_form.is_valid() and coupon_form.is_valid():
      succeed, exception = services.checkout(order, shipping_form, coupon_form)
      if succeed:
        messages.success(request, message='Thanh toán thành công')
        return redirect('checkout_result', order_id=order_id)
      else:
        messages.error(request, message='Thanh toán thất bại')

  context['shipping_form'] = shipping_form
  context['coupon_form'] = coupon_form

  return TemplateResponse(request, 'store/checkout.html', context)

@partners_only
def checkout_result(request, order_id):
  order = services.get_none_draft_orders(pk=order_id, customer=request.partner).first()
  if not order:
    messages.error(request, message=f'Đơn hàng không tồn tại')
  else:
    messages.success(request, message=f'Đơn hàng {order_id} đang được xử lý')

  return TemplateResponse(request, 'store/checkout-result.html', { 'title': 'Kết quả thanh toán' })

def login(request):
  next_url = request.GET.get('next', reverse('index'))

  if request.session.get('partner_id'):
    return redirect(next_url)

  context = { 'title': 'Đăng nhập' }

  form = forms.LoginForm()

  if request.user.is_authenticated and request.user.email:
    user_form = forms.LoginUserForm({ 'email': request.user.email })
    context['user_form'] = user_form

  if request.method == 'POST':
    form = forms.LoginForm(request.POST)

    if form.is_valid():
      if settings.F2A_ENABLE:
        # Begin storing form_login and otp to session
        if services.generate_otp(request):
          services.save_temporary_login_form(request, form)
          return redirect(reverse('login_otp') + f'?next={next_url}')
        else:
          form.add_error(None, 'Hệ thống không thể tạo OTP vào lúc này')
      else:
        # Synchrozire local shopping_cart with database
        succeed, partner, exception = services.sync_shopping_cart(form.cleaned_data['email'], form.cleaned_data['shopping_cart'])

        if succeed:
          request.session['partner_id'] = partner.id
          return redirect(next_url)
        else:
          form.add_error(None, exception.args)
  
  context['form'] = form

  return TemplateResponse(request, 'store/accounts/login.html', context)

@login_required
def login_user(request):
  next_url = request.GET.get('next', 'index')

  if request.session.get('partner_id'):
    return redirect(next_url)

  login_form = forms.LoginUserForm(request.POST)
  if login_form.is_valid():
    succeed, partner, exception = services.login_user(request, login_form.cleaned_data['email'])
    if succeed:
      request.session['partner_id'] = partner.id
      return redirect(next_url)
    else:
      messages.error(request, exception.args)
  
  return TemplateResponse(request, 'store/accounts/login.html', {})

def login_otp(request):
  next_url = request.GET.get('next', reverse('index'))

  if request.session.get('partner_id'):
    return redirect(next_url)
  
  if not request.session['otp_code']:
    return redirect('login')
  
  context = { 'title': 'Đăng nhập - OTP' }

  login_otp_form = forms.LoginOtpForm()

  if request.method == 'POST':
    login_otp_form = forms.LoginOtpForm(request.POST)
    if login_otp_form.is_valid():
      otp_code_input = login_otp_form.cleaned_data['otp_code']
      if services.validate_otp(request, otp_code_input):
        # Synchrozire local shopping_cart with database
        succeed, partner, exception = services.sync_shopping_cart(request.session.get('login_form_email'), request.session.get('login_form_shopping_cart'))

        if succeed:
          request.session['partner_id'] = partner.id

          # Finish storing form_login and otp to session
          services.clear_temporary_data_after_login(request)

          return redirect(next_url)
        else:
          login_otp_form.add_error(None, exception.args)
      else:
        login_otp_form.add_error(None, 'Mã OTP không chính xác hoặc quá hạn')

  context['login_otp_form'] = login_otp_form

  return TemplateResponse(request, 'store/accounts/otp.html', context)

def resend_otp(request):
  succeed = services.generate_otp(request)
  if not succeed:
    messages.error(request, message='Hệ thống không thể tạo OTP vào lúc này')
  return redirect('login_otp')

def logout(request):
  if request.session.get('partner_id'):
    request.session.__delitem__('partner_id')
    return redirect('login')
  return redirect('index')

def register(request):
  form = forms.RegisterForm()

  if request.method == 'POST':
    form = forms.RegisterForm(request.POST)
    if form.is_valid():
      succeed, partner, exception = services.register(form.cleaned_data['email'], form.cleaned_data['phone'])
      if succeed:
        return redirect('login')
      else:
        form.add_error(None, exception.args)

  return TemplateResponse(request, 'store/accounts/register.html', { 'form': form, 'title': 'Đăng ký tài khoản' })

@partners_only
def profile(request):
  form = forms.ProfileForm(instance=request.partner)
  queryset = services.get_address_by_customer(request.partner)
  address_formset = forms.AddressFormSet(queryset=queryset)

  if request.method == 'POST':
    which_form = request.GET.get('form')
    if which_form == 'profile_form':
      form = forms.ProfileForm(request.POST, instance=request.partner)
      if form.is_valid():
        try:
          form.save()
          messages.success(request, 'Cập nhật thông tin thành công!')
        except Exception as e:
          form.add_error(None, e.args)

    if which_form == 'address_form':
      address_formset = forms.AddressFormSet(request.POST, queryset=queryset)
      if address_formset.is_valid():
        instances = address_formset.save()
        # or
        # instances = address_formset.save(commit=False)
        # for instance in instances:
        #   instance.save()
    
  return TemplateResponse(request, 'store/accounts/profile.html', { 'form': form, 'address_formset': address_formset, 'title': 'Quản lý thông tin cá nhân' })
