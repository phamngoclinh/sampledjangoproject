from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from .decorators import partners_only

from .forms import AddressFormSet, ProfileForm, LoginForm, LoginUserForm, RegisterForm, ShippingForm, CouponForm

from . import services

def index(request):
  context = { 'products': services.get_all_products() }
  return TemplateResponse(request, 'store/index.html', context)

def product_category(request, category_id):
  context = { 'products': services.get_products_in_category(category_id) }
  return TemplateResponse(request, 'store/product_category.html', context)

def product_detail(request, product_id):
  context = { 'product': services.get_product_by_id(product_id) }
  return TemplateResponse(request, 'store/product_detail.html', context)

def search(request):
  product_name = request.GET.get('product_name', '')
  context = { 'products': services.search_product(product_name) }
  return TemplateResponse(request, 'store/search.html', context)

def shopping_cart(request):
  return TemplateResponse(request, 'store/shopping-cart.html', {})

@partners_only
def orders(request):
  context = { 'orders': services.get_none_draft_orders(customer=request.partner).order_by('-created_date') }
  return TemplateResponse(request, 'store/orders.html', context)

@partners_only
def order(request, order_id):
  context = {}
  order = services.get_partner_order_by_id(order_id, request.partner)
  context['order'] = order
  if order:
    context['deliveries'] = services.get_order_delivers_by_order(order)
  return TemplateResponse(request, 'store/order.html', context)

@partners_only
def checkout(request, order_id):
  order = services.get_draft_order(pk=order_id)
  
  if not order or (order.customer != request.partner):
    return redirect('checkout_result', order_id=order_id)
  
  context = {
    # 'coupon_programs': services.get_available_coupon_programs(),
    'shipping_addresses': services.get_address_by_customer(request.partner),
  }

  shipping = {
    'city': order.shipping_address and order.shipping_address.city or '',
    'district': order.shipping_address and order.shipping_address.district or '',
    'award': order.shipping_address and order.shipping_address.award or '',
    'address': order.shipping_address and order.shipping_address.address or '',
    'receive_name': order.receive_name or order.customer.full_name,
    'receive_phone': order.receive_phone or order.customer.phone,
    'receive_email': order.receive_email or order.customer.email,
    'note': order.note or '',
  }
  shipping_form = ShippingForm(shipping)

  coupon = services.get_coupon_by_order(order)
  if coupon:
    coupon_form = CouponForm({ 'code': coupon.code, 'coupon_program_id': coupon.program.id })
  else:
    coupon_form = CouponForm()

  if request.method == 'POST':
    shipping_form = ShippingForm(request.POST)
    coupon_form = CouponForm(request.POST)
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

  return TemplateResponse(request, 'store/checkout-result.html', {})

def login(request):
  next_url = request.GET.get('next', 'index')

  if request.session.get('partner_id'):
    return redirect(next_url)

  context = {}

  form = LoginForm()

  if request.method == 'POST':
    form = LoginForm(request.POST)

    if form.is_valid():
      # Synchrozire local shopping_cart with database
      succeed, partner, exception = services.sync_shopping_cart(form.cleaned_data['email'], form.cleaned_data['shopping_cart'])

      if succeed:
        request.session['partner_id'] = partner.id
        return redirect(next_url)
      else:
        form.add_error(None, exception.args)
  
  context['form'] = form

  if request.user.is_authenticated and request.user.email:
    user_form = LoginUserForm({ 'email': request.user.email })
    context['user_form'] = user_form

  return TemplateResponse(request, 'store/accounts/login.html', context)

@login_required
def login_user(request):
  next_url = request.GET.get('next', 'index')

  if request.session.get('partner_id'):
    return redirect(next_url)

  login_form = LoginUserForm(request.POST)
  if login_form.is_valid():
    succeed, partner, exception = services.login_user(request, login_form.cleaned_data['email'])
    if succeed:
      request.session['partner_id'] = partner.id
      return redirect(next_url)
    else:
      messages.error(request, exception.args)
  
  return TemplateResponse(request, 'store/accounts/login.html', {})

def logout(request):
  if request.session.get('partner_id'):
    request.session.__delitem__('partner_id')
    return redirect('login')
  return redirect('index')

def register(request):
  form = RegisterForm()

  if request.method == 'POST':
    form = RegisterForm(request.POST)
    if form.is_valid():
      succeed, partner, exception = services.register(form.cleaned_data['email'], form.cleaned_data['phone'])
      if succeed:
        return redirect('login')
      else:
        form.add_error(None, exception.args)

  return TemplateResponse(request, 'store/accounts/register.html', { 'form': form })

@partners_only
def profile(request):
  form = ProfileForm(instance=request.partner)
  queryset = services.get_address_by_customer(request.partner)
  address_formset = AddressFormSet(queryset=queryset)

  if request.method == 'POST':
    which_form = request.GET.get('form')
    if which_form == 'profile_form':
      form = ProfileForm(request.POST, instance=request.partner)
      if form.is_valid():
        try:
          form.save()
          messages.success(request, 'Cập nhật thông tin thành công!')
        except Exception as e:
          form.add_error(None, e.args)

    if which_form == 'address_form':
      address_formset = AddressFormSet(request.POST, queryset=queryset)
      if address_formset.is_valid():
        instances = address_formset.save()
        # or
        # instances = address_formset.save(commit=False)
        # for instance in instances:
        #   instance.save()
    
  return TemplateResponse(request, 'store/accounts/profile.html', { 'form': form, 'address_formset': address_formset })
