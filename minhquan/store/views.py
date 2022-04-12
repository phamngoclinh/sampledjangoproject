import json

from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import redirect, render
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
  context = { 'title': 'Home' }

  products = Product.objects.all()

  if request.partner:
    user_email = request.partner.email
  else:
    user_email = None
  
  try:
    pos = POS.objects.get(customer__email=user_email)
  except POS.DoesNotExist:
    pos = None
  
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
  else:
    user_email = None

  try:
    pos = POS.objects.get(customer__email=user_email)
  except POS.DoesNotExist:
    pos = None
  
  context['pos'] = pos
  context['products'] = products
  context['product_categories'] = get_custom_product_categories()

  return render(request, 'store/product_category.html', context)

def product_detail(request, product_id):
  context = { 'title': 'Product detail' }

  product = Product.objects.get(pk=product_id)

  if request.partner:
    user_email = request.partner.email
  else:
    user_email = None

  try:
    pos = POS.objects.get(customer__email=user_email)
  except POS.DoesNotExist:
    pos = None
  
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
  else:
    user_email = None

  try:
    pos = POS.objects.get(customer__email=user_email)
  except POS.DoesNotExist:
    pos = None
  
  context['pos'] = pos
  context['products'] = products
  context['product_categories'] = get_custom_product_categories()

  return render(request, 'store/search.html', context)

def cart_detail(request):
  context = { 'title': 'Cart' }

  if request.partner:
    user_email = request.partner.email
  else:
    user_email = None

  try:
    pos = POS.objects.get(customer__email=user_email)
  except POS.DoesNotExist:
    pos = None
  
  context['pos'] = pos

  return render(request, 'store/cart_detail.html', context)

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
    pos, is_now_pos = POS.objects.get_or_create(customer_id=customer.id)

    posdetail, is_new_posdetail = pos.posdetail_set.get_or_create(product_id=product.id)
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

@require_http_methods(['GET', 'POST'])
def login(request):
  if request.session.get('partner_id'):
    return redirect('index')

  if request.method == 'GET':
    return render(request, 'store/accounts/login.html', {})
  
  email = request.POST.get('email')
  if not email:
    return render(request, 'store/accounts/login.html', { 'messages': 'Email không được bỏ trống' })
  
  try:
    partner = Partner.objects.get(email=email)
  except Partner.DoesNotExist:
    return render(request, 'store/accounts/login.html', { 'messages': f'{email} không tồn tại' })
    
  request.session['partner_id'] = partner.id
  return redirect('index')

def logout(request):
  if request.session.get('partner_id'):
    request.session.__delitem__('partner_id')
    return redirect('login')
  return redirect('index')
  
@require_http_methods(['GET', 'POST'])
def register(request):
  context = {}

  if request.method == 'POST':
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    full_name = request.POST.get('full_name')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    dob = request.POST.get('dob')

    if not email:
      context['messages'] = 'Email không được bỏ trống'
    elif not phone:
      context['messages'] = 'Điện thoại không được bỏ trống'
    else:
      partners = Partner.objects.filter(Q(email=email) | Q(phone=phone))
      if partners:
        context['messages'] = 'Email hoặc điện thoại đã tồn tại'
        return render(request, 'store/accounts/register.html', context)
      try:
        Partner.objects.create(
          email=email,
          phone=phone,
          full_name=full_name if full_name else last_name + ' ' + first_name,
          first_name=first_name,
          last_name=last_name,
          dob=dob
        )
        return redirect('login')
      except Exception as e:
        context['messages'] = e.args

  return render(request, 'store/accounts/register.html', context)

