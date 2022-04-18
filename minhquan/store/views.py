from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from .forms import ProfileForm, LoginForm, LoginUserForm, RegisterForm, ShippingForm, CouponForm

from . import services

def index(request):
  context = { 'title': 'Home' }

  context['products'] = services.get_all_products()
  
  return TemplateResponse(request, 'store/index.html', context)

def product_category(request, category_id):
  context = { 'title': 'Product category' }

  context['products'] = services.get_products_in_category(category_id)

  return TemplateResponse(request, 'store/product_category.html', context)

def product_detail(request, product_id):
  context = { 'title': 'Product detail' }

  context['product'] = services.get_product_by_id(product_id)

  return TemplateResponse(request, 'store/product_detail.html', context)

def search(request):
  context = { 'title': 'Search' }
  
  product_name = request.GET.get('product_name', '')
  context['products'] = services.search_product(product_name)

  return TemplateResponse(request, 'store/search.html', context)

def cart(request):
  context = { 'title': 'Cart' }

  return TemplateResponse(request, 'store/cart.html', context)

def carts(request):
  context = { 'title': 'Carts' }

  if request.partner:
    user_email = request.partner.email
    context['carts'] = services.get_none_draft_orders(customer__email=user_email)

  return TemplateResponse(request, 'store/carts.html', context)

def checkout(request, order_id):
  context = { 'title': 'Checkout' }

  if request.partner:
    order = services.get_draft_order(pk=order_id)
    
    if not order:
      return redirect('checkout_success', order_id=order_id)

    # validate order_customer is current partner here
    # TODO

    context['cart'] = order
    # context['coupon_programs'] = services.get_available_coupon_programs()
    context['shipping_addresses'] = services.get_address_by_customer(request.partner)

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

    context['shipping_form'] = shipping_form
    context['coupon_form'] = coupon_form

  return TemplateResponse(request, 'store/checkout.html', context)

def checkout_success(request, order_id):
  context = { 'title': 'Checkout' }

  context['cart'] = services.get_none_draft_orders(pk=order_id)  

  return TemplateResponse(request, 'store/checkout-success.html', context)

def login(request):
  if request.session.get('partner_id'):
    return redirect('index')

  context = {}

  form = LoginForm()

  if request.method == 'POST':
    form = LoginForm(request.POST)

    if form.is_valid():
      # Synchrozire local shopping_cart with database
      succeed, partner, exception = services.sync_shopping_cart(form.cleaned_data['email'], form.cleaned_data['shopping_cart'])

      if succeed:
        request.session['partner_id'] = partner.id
        return redirect('index')
      else:
        form.add_error(None, exception.args)
  
  context['form'] = form

  if request.user.is_authenticated and request.user.email:
    user_form = LoginUserForm({ 'email': request.user.email })
    context['user_form'] = user_form

  return TemplateResponse(request, 'store/accounts/login.html', context)

@login_required
def login_user(request):
  if request.session.get('partner_id'):
    return redirect('index')
  login_form = LoginUserForm(request.POST)
  if login_form.is_valid():
    succeed, partner, exception = services.login_user(request, login_form.cleaned_data['email'])
    if succeed:
      request.session['partner_id'] = partner.id
      return redirect('index')
    else:
      messages.error(request, exception.args)

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

def profile(request):
  if not request.partner:
    return redirect('index')

  partner = services.get_partner_by_email(request.partner.email)

  form = ProfileForm(instance=partner)

  if request.method == 'POST':
    form = ProfileForm(request.POST, instance=partner)
    if form.is_valid():
      try:
        form.save()
        messages.success(request, 'Cập nhật thông tin thành công!')
      except Exception as e:
        form.add_error(None, e.args)

  return TemplateResponse(request, 'store/accounts/profile.html', { 'form': form })
