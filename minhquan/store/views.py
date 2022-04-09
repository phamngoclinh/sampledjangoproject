from django.shortcuts import render
from django.db.models import Q
from datetime import datetime
from .models import CouponProgram, Product, ProductCategory

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

def get_product_categories():
  product_categories_tree = convert_categories_into_tree(ProductCategory.objects.values())
  return product_categories_tree

def get_coupon_programs():
  return CouponProgram.objects.filter(start_date__lte=datetime.today(), expired_date__gte=datetime.today())

def get_coupon_programs_by_product_id(product_id, coupon_programs):
  product_coupon_programs = []
  for coupon_program in coupon_programs:
    for product in coupon_program.products:
      if product.id == product_id:
        sub_price = coupon_program.discount_price(product.price)
        product_coupon_programs.append({
          'data': coupon_program,
          'populated': {
            'sub_price': sub_price
          }
        })
  return product_coupon_programs

def get_products():
  products = []
  coupon_programs = get_coupon_programs()
  for product in Product.objects.all():
    product_coupon_programs = get_coupon_programs_by_product_id(product.id, coupon_programs)
    products.append({
      'data': product,
      'coupon_programs': product_coupon_programs
    })
  return products

def index(request):
  products = get_products()

  return render(request, 'store/index.html', {
    'title': 'Home',
    'product_categories': get_product_categories(),
    'products': products
  })

def product_category(request, category_id):
  category = ProductCategory.objects.get(id=category_id)
  category_childrens = category.get_childrens()
  category_children_ids = [i.id for i in category_childrens]
  products = Product.objects.filter(Q(category_id__in=category_children_ids) | Q(category_id=category_id))
  return render(request, 'store/product_category.html', {
    'title': 'Product category',
    'product_categories': get_product_categories(),
    'products': products
  })

def product_detail(request, product_id):
  coupon_programs = get_coupon_programs()
  product_coupon_programs = get_coupon_programs_by_product_id(product_id, coupon_programs)
  product = Product.objects.get(pk=product_id)

  return render(request, 'store/product_detail.html', {
    'title': 'Product detail',
    'product_categories': get_product_categories(),
    'product': product,
    'coupon_programs': product_coupon_programs
  })

def cart_detail(request):
  return render(request, 'store/cart_detail.html', {
    'title': 'Cart'
  })
