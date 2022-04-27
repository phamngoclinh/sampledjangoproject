import json
from datetime import datetime

from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Order, Coupon, Partner, Product

from . import services

from . import forms


@csrf_exempt
@require_http_methods(['POST'])
def get_coupon(request):
  try:
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    code = body['code']
    coupon = Coupon.objects.get(
      code=code,
      order__isnull=True,
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

    product = services.get_or_none(Product, pk=body['product_id'])
    if not product:
      return JsonResponse({ 'success': False, 'messages': 'Sản phẩm không tồn tại' })

    customer, is_new_customer = Partner.objects.get_or_create(email=user_email)
    order = services.get_draft_order(customer=customer)
    if not order:
      order = Order.objects.create(customer=customer)

    orderdetail, is_new_orderdetail = order.orderdetails.get_or_create(
      product_id=product.id,
      defaults={
        'price_unit': product.price,
        'sub_price_unit': product.sub_price
      }
    )
    
    if is_new_orderdetail:
      orderdetail.save()
    else:
      if 'quantity' not in body:
        orderdetail.quantity += 1
        orderdetail.save()
      else:
        quantity = body['quantity']
        if quantity: # set a specific quantity
          orderdetail.quantity = quantity
          orderdetail.save()
        else: # delete order detail
          orderdetail.delete()

    order.save()

    return JsonResponse({
      'success': True,
      'order': model_to_dict(order),
      'order_count': order.orderdetails.count(),
      'orderdetail': model_to_dict(orderdetail),
      'product': {
        'id': orderdetail.product.id,
        'price': orderdetail.product.price,
        'discount_price': orderdetail.product.sub_price
      },
    })
  except Exception as e:
    return JsonResponse({ 'success': False, 'messages': e.args })

@csrf_exempt
@require_http_methods(['POST'])
def get_product(request):
  try:
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    product_id = body['product_id']
    product = services.get_product_by_id(product_id)
    return JsonResponse({
      'success': True,
      'product': {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'price': product.price,
        'sub_price': product.sub_price,
        'price_discount': product.price_discount,
      }
    })
  except Product.DoesNotExist:
    return JsonResponse({ 'success': False, 'messages': 'Sản phầm không tồn tại' })

@csrf_exempt
@require_http_methods(['POST'])
def search_product(request):
  try:
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    search_text = body['search_text']
    products = services.search_product(search_text)
    return JsonResponse({
      'success': True,
      'data': list({
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'price': product.price,
        'sub_price': product.sub_price,
        'price_discount': product.price_discount,
      } for product in products)
    })
  except Product.DoesNotExist:
    return JsonResponse({ 'success': False, 'messages': 'Không tìm thấy sản phẩm' })

@csrf_exempt
@require_http_methods(['POST'])
def search_partner(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)

  search_text = body['search_text']
  partner = services.search_partner(search_text)
  return JsonResponse({
    'success': True,
    'data': list(partner.values())
  })

@csrf_exempt
@require_http_methods(['POST'])
def search_address(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)

  search_text = body['search_text']
  if 'customer' in body:
    address = services.search_address_by_partner(search_text, body['customer'])
  else:
    address = services.search_address(search_text)
  return JsonResponse({
    'success': True,
    'data': list(address.values())
  })

@csrf_exempt
@require_http_methods(['POST'])
def create_partner(request):
  form = forms.RegisterForm(request.POST)
  if form.is_valid():
    succeed, partner, exception = services.register(form.cleaned_data['email'], form.cleaned_data['phone'])
    if succeed:
      return JsonResponse({
        'success': True,
        'data': model_to_dict(partner),
        'form': form.as_table()
      })
    else:
      return JsonResponse({
        'success': False,
        'form': form.as_table(),
        'messages': exception.args
      })
  return JsonResponse({
    'success': False,
    'form': form.as_table(),
    'messages': 'Creating a partner was failed'
  })

@csrf_exempt
@require_http_methods(['POST'])
def create_address(request):
  form = forms.AddressModelForm(request.POST)
  if form.is_valid():
    address = form.save()
    return JsonResponse({
      'success': True,
      'data': model_to_dict(address),
      'form': form.as_table()
    })
  return JsonResponse({
    'success': False,
    'form': form.as_table(),
    'messages': 'Creating a address was failed'
  })



urlpatterns = [
  path('get-coupon/', get_coupon, name='get_coupon'),
  path('add-to-cart/', add_to_cart, name='add_to_cart'),
  path('get-product/', get_product, name='get_product'),
  path('search-product/', search_product, name='search_product'),
  path('search-customer/', search_partner, name='search_partner'),
  path('search-shipping_address/', search_address, name='search_address'),
  path('create-partner/', create_partner, name='create_partner'),
  path('create-address/', create_address, name='create_address'),
]