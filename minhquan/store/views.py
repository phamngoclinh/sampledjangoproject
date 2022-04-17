import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import ProfileForm, LoginForm, LoginUserForm, RegisterForm, ShippingForm, CouponForm

from .models import POS, Address, Coupon, CouponProgram, POSDetail, Partner, Product, ProductCategory


def convert_categories_into_tree(categories):
  map, roots = {}, []
  for i, item in enumerate(categories):
    map[item['id']] = i
    item['children'] = []
  for i, item in enumerate(categories):
    if item['parent_id']:
      categories[map[item['parent_id']]]['children'].append(item)
    else:
      roots.append(item)
  return roots

def get_custom_product_categories():
  product_categories_tree = convert_categories_into_tree(ProductCategory.objects.values())
  return product_categories_tree

def get_or_none(classmodel, **kwargs):
  try:
    return classmodel.objects.get(**kwargs)
  except classmodel.DoesNotExist:
    return None

def index(request):
  context = { 'title': 'Home' }

  products = Product.objects.all()

  if request.partner:
    user_email = request.partner.email
    pos = get_or_none(POS, customer__email=user_email, status='draft')
    context['pos'] = pos
  
  context['products'] = products
  context['product_categories'] = get_custom_product_categories()
  
  return render(request, 'store/index.html', context)

def product_category(request, category_id):
  context = { 'title': 'Product category' }

  category = ProductCategory.objects.get(id=category_id)
  category_childrens = category.get_childrens()
  category_children_ids = [i.id for i in category_childrens]
  products = Product.objects.filter(Q(category_id__in=category_children_ids) | Q(category_id=category_id))
  
  if request.partner:
    user_email = request.partner.email
    pos = get_or_none(POS, customer__email=user_email, status='draft')
    context['pos'] = pos

  context['products'] = products
  context['product_categories'] = get_custom_product_categories()

  return render(request, 'store/product_category.html', context)

def product_detail(request, product_id):
  context = { 'title': 'Product detail' }

  product = Product.objects.get(pk=product_id)

  if request.partner:
    user_email = request.partner.email
    pos = get_or_none(POS, customer__email=user_email, status='draft')
    context['pos'] = pos

  context['product'] = product
  context['product_categories'] = get_custom_product_categories()

  return render(request, 'store/product_detail.html', context)

def search(request):
  context = { 'title': 'Search' }

  product_name = request.GET.get('product_name', '')
  products = Product.objects.filter(Q(name__icontains=product_name) | Q(slug__icontains=product_name))

  if request.partner:
    user_email = request.partner.email
    pos = get_or_none(POS, customer__email=user_email, status='draft')
    context['pos'] = pos
  
  context['products'] = products
  context['product_categories'] = get_custom_product_categories()

  return render(request, 'store/search.html', context)

def cart(request):
  context = { 'title': 'Cart' }

  if request.partner:
    user_email = request.partner.email
    pos = get_or_none(POS, customer__email=user_email, status='draft')
    context['pos'] = pos

  return render(request, 'store/cart.html', context)

def carts(request):
  context = { 'title': 'Carts' }

  if request.partner:
    user_email = request.partner.email
    carts = POS.objects.filter(customer__email=user_email).exclude(status='draft')
    pos = get_or_none(POS, customer__email=user_email, status='draft')
    context['pos'] = pos
    context['carts'] = carts

  return render(request, 'store/carts.html', context)

@require_http_methods(['GET', 'POST'])
def checkout(request, pos_id):
  context = { 'title': 'Checkout' }

  if request.partner:
    user_email = request.partner.email
    pos = get_object_or_404(POS, pk=pos_id, customer__email=user_email)
    context.update({
      'cart': pos,
      'pos': pos
    })
    if pos.status != 'draft':
      return redirect('checkout_success', pos_id=pos.id)

    coupon_programs = CouponProgram.objects.filter(start_date__lte=datetime.today(), expired_date__gte=datetime.today())
    context['coupon_programs'] = coupon_programs

    partner_poss = POS.objects.filter(customer__email=user_email).only('shipping_address_id')
    shipping_address_ids = []
    for partner_pos in partner_poss:
      shipping_address_ids.append(partner_pos.shipping_address_id)
    shipping_addresses = Address.objects.filter(pk__in=shipping_address_ids)
    context['shipping_addresses'] = shipping_addresses

    shipping = {
      'city': pos.shipping_address and pos.shipping_address.city or '',
      'district': pos.shipping_address and pos.shipping_address.district or '',
      'award': pos.shipping_address and pos.shipping_address.award or '',
      'address': pos.shipping_address and pos.shipping_address.address or '',
      'receive_name': pos.receive_name or pos.customer.full_name,
      'receive_phone': pos.receive_phone or pos.customer.phone,
      'receive_email': pos.receive_email or pos.customer.email,
      'note': pos.note or '',
    }
    shipping_form = ShippingForm(shipping)

    coupon = get_or_none(Coupon, pos=pos)
    if coupon:
      coupon_form = CouponForm({ 'code': coupon.code, 'coupon_program_id': coupon.program.id })
    else:
      coupon_form = CouponForm()

    if request.method == 'POST':
      shipping_form = ShippingForm(request.POST)
      coupon_form = CouponForm(request.POST)
      if shipping_form.is_valid() and coupon_form.is_valid():
        # Save shipping information
        if coupon_form.cleaned_data['code']:
          coupon = Coupon.objects.get(code=coupon_form.cleaned_data['code'])
          coupon.pos = pos
          coupon.save()

        if shipping_form.cleaned_data['address_id']:
          address = Address.objects.get(pk=shipping_form.cleaned_data['address_id'])
          address.city=shipping_form.cleaned_data['city']
          address.district=shipping_form.cleaned_data['district']
          address.award=shipping_form.cleaned_data['award']
          address.address=shipping_form.cleaned_data['address']
          address.save()
        else:
          address = Address.objects.create(
            city=shipping_form.cleaned_data['city'],
            district=shipping_form.cleaned_data['district'],
            award=shipping_form.cleaned_data['award'],
            address=shipping_form.cleaned_data['address'],
          )
        pos.receive_name = shipping_form.cleaned_data['receive_name']
        pos.receive_phone = shipping_form.cleaned_data['receive_phone']
        pos.receive_email = shipping_form.cleaned_data['receive_email']
        pos.note = shipping_form.cleaned_data['note']
        pos.shipping_address = address
        pos.status = 'processing'
        pos.calculate()
        pos.save()
        # Update coupon program

    context['shipping_form'] = shipping_form
    context['coupon_form'] = coupon_form

  return render(request, 'store/checkout.html', context)

def checkout_success(request, pos_id):
  context = { 'title': 'Checkout' }

  if request.partner:
    user_email = request.partner.email
    pos = get_object_or_404(POS, pk=pos_id, customer__email=user_email)
    context.update({
      'cart': pos,
      'pos': pos
    })
  return render(request, 'store/checkout-success.html', context)

@csrf_exempt
@require_http_methods(['POST'])
def get_coupon(request):
  try:
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    code = body['code']
    coupon = Coupon.objects.get(
      code=code,
      pos__isnull=True,
      program__start_date__lte=datetime.today(),
      program__expired_date__gte=datetime.today()
    )
    return JsonResponse({
      'success': True,
      'discount_type': coupon.program.discount_type,
      'discount': coupon.program.discount,
    })
  except Coupon.DoesNotExist:
    return JsonResponse({ 'success': False, 'messages': 'Mã giảm giá không tồn tại' })  


@csrf_exempt
@require_http_methods(['POST'])
def add_to_cart(request):
  try:
    if request.partner:
      user_email = request.partner.email
    else:
      user_email = None

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    try:
      product_id = body['product_id']
      product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
      return JsonResponse({ 'success': False, 'messages': 'Sản phẩm không tồn tại' })

    customer, is_new_customer = Partner.objects.get_or_create(email=user_email)
    pos, is_now_pos = POS.objects.get_or_create(customer_id=customer.id, status='draft')

    posdetail, is_new_posdetail = pos.posdetail_set.get_or_create(
      product_id=product.id,
      defaults={
        'price_unit': product.price,
        'sub_price_unit': product.sub_price
      }
    )
    
    if is_new_posdetail:
      posdetail.calculate()
      posdetail.save()
    else:
      if 'quantity' not in body:
        posdetail.quantity += 1
        posdetail.calculate()
        posdetail.save()
      else:
        quantity = body['quantity']
        if quantity: # set a specific quantity
          posdetail.quantity = quantity
          posdetail.calculate()
          posdetail.save()
        else: # delete pos detail
          posdetail.delete()

    pos.calculate()
    pos.save()

    return JsonResponse({
      'success': True,
      'pos': model_to_dict(pos),
      'pos_count': pos.posdetail_set.count(),
      'posdetail': model_to_dict(posdetail),
      'product': {
        'id': posdetail.product.id,
        'price': posdetail.product.price,
        'discount_price': posdetail.product.sub_price
      },
    })
  except Exception as e:
    return JsonResponse({ 'success': False, 'messages': e.args })

def sync_shopping_cart(partner, shopping_cart):
  pos, is_new_pos = POS.objects.get_or_create(customer=partner, status='draft')

  total = pos.amount_sub_total
  for sp_posdetail in shopping_cart['pos']['posdetails']:
    product = Product.objects.get(pk=sp_posdetail['product']['id'])
    posdetail, is_new_posdetail = POSDetail.objects.get_or_create(
      pos=pos,
      product=product,
      defaults={
        'quantity': sp_posdetail['quantity'],
        'price_unit': product.price,
        'sub_price_unit': product.sub_price,
        'price_discount': sp_posdetail['quantity'] * (product.price - product.sub_price),
        'amount_price': sp_posdetail['quantity'] * product.price,
        'sub_total': sp_posdetail['quantity'] * product.sub_price if product.sub_price else sp_posdetail['quantity'] * product.price
      }
    )

    if not is_new_posdetail:
      posdetail.quantity += sp_posdetail['quantity']
      posdetail.amount_price = posdetail.quantity * posdetail.price_unit
      posdetail.price_discount = posdetail.quantity * (posdetail.price_unit - posdetail.sub_price_unit)
      posdetail.sub_total = posdetail.quantity * posdetail.sub_price_unit if posdetail.sub_price_unit else posdetail.quantity * posdetail.price_unit
      posdetail.save()
    
    total += posdetail.sub_total

  if (pos.amount_sub_total != total):
    pos.calculate()
    pos.save()

@require_http_methods(['GET', 'POST'])
def login(request):
  if request.session.get('partner_id'):
    return redirect('index')

  context = {}

  form = LoginForm()

  if request.method == 'POST':
    form = LoginForm(request.POST)

    if form.is_valid():
      try:
        email = form.cleaned_data['email']
        
        # Synchrozire local shopping_cart with database
        partner = Partner.objects.get(email=email)
        shopping_cart = form.cleaned_data['shopping_cart']
        sync_shopping_cart(partner, shopping_cart)

        request.session['partner_id'] = partner.id
        return redirect('index')
      except Exception as e:
        form.add_error(None, e.args)
  
  context['form'] = form

  if request.user.is_authenticated and request.user.email:
    user_form = LoginUserForm({ 'email': request.user.email })
    context['user_form'] = user_form

  return render(request, 'store/accounts/login.html', context)

@login_required
@require_http_methods(['POST'])
def login_user(request):
  if request.session.get('partner_id'):
    return redirect('index')
  login_form = LoginUserForm(request.POST)
  if login_form.is_valid():
    try:
      partner, is_new = Partner.objects.get_or_create(email=login_form.cleaned_data['email'])
      if is_new:
        partner.user = request.user
        partner.save()
      request.session['partner_id'] = partner.id
      return redirect('index')
    except Exception as e:
      messages.error(request, e.args)
  return redirect('login')

def logout(request):
  if request.session.get('partner_id'):
    request.session.__delitem__('partner_id')
    return redirect('login')
  return redirect('index')
  
@require_http_methods(['GET', 'POST'])
def register(request):
  form = RegisterForm()

  if request.method == 'POST':
    form = RegisterForm(request.POST)
    if form.is_valid():
      try:
        Partner.objects.create(
          email=form.cleaned_data['email'],
          phone=form.cleaned_data['phone']
        )
        return redirect('login')
      except Exception as e:
        form.add_error(None, e.args)

  return render(request, 'store/accounts/register.html', { 'form': form })

@require_http_methods(['GET', 'POST'])
def profile(request):
  if not request.partner:
    return redirect('index')

  partner = Partner.objects.get(email=request.partner.email)

  form = ProfileForm(instance=partner)

  if request.method == 'POST':
    form = ProfileForm(request.POST, instance=partner)
    if form.is_valid():
      try:
        form.save()
        messages.success(request, 'Cập nhật thông tin thành công!')
      except Exception as e:
        form.add_error(None, e.args)

  return render(request, 'store/accounts/profile.html', { 'form': form })

