import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import POS, Partner, Product, ProductCategory


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

def index(request):
  products = Product.objects.all()
  pos = POS.objects.get(customer_id=request.user.id)
  return render(request, 'store/index.html', {
    'title': 'Home',
    'product_categories': get_custom_product_categories(),
    'products': products,
    'pos': pos
  })

def product_category(request, category_id):
  category = ProductCategory.objects.get(id=category_id)
  category_childrens = category.get_childrens()
  category_children_ids = [i.id for i in category_childrens]
  products = Product.objects.filter(Q(category_id__in=category_children_ids) | Q(category_id=category_id))
  pos = POS.objects.get(customer_id=request.user.id)
  return render(request, 'store/product_category.html', {
    'title': 'Product category',
    'product_categories': get_custom_product_categories(),
    'products': products,
    'pos': pos,
  })

def product_detail(request, product_id):
  product = Product.objects.get(pk=product_id)
  pos = POS.objects.get(customer_id=request.user.id)
  return render(request, 'store/product_detail.html', {
    'title': 'Product detail',
    'product_categories': get_custom_product_categories(),
    'product': product,
    'pos': pos,
  })

def search(request):
  product_name = request.GET.get('product_name', '')
  products = Product.objects.filter(Q(name__icontains=product_name) | Q(slug__icontains=product_name))
  return render(request, 'store/search.html', {
    'title': 'Search',
    'product_categories': get_custom_product_categories(),
    'products': products
  })

def cart_detail(request):
  pos = POS.objects.get(customer_id=request.user.id)
  context = {
    'title': 'Cart',
    'pos': pos
  }
  return render(request, 'store/cart_detail.html', context)

@login_required
@csrf_exempt
@require_http_methods(['POST'])
def add_to_cart(request):
  try:
    user = request.user
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    product_id = body['product_id']
    product = Product.objects.get(pk=product_id)

    if not product:
      return JsonResponse({ 'success': False, 'messages': 'product_id is not exists' })

    pos, is_now_pos = POS.objects.get_or_create(customer_id=user.id)
    customer, is_new_customer = Partner.objects.get_or_create(email=user.email)
    pos.customer = customer

    posdetail, is_new_posdetail = pos.posdetail_set.get_or_create(product_id=product_id)
    if 'quantity' not in body: # increase quantity
      if not is_new_posdetail:
        posdetail.quantity += 1
        posdetail.save()
    else: # set quantity or delete
      quantity = body['quantity']
      if quantity: # set a specific quantity
        posdetail.quantity = quantity
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
        'discount_price': posdetail.product.discount_price()
      },
    })
  except Exception as e:
    return JsonResponse({ 'success': False, 'messages': e.args })
