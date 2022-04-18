from datetime import datetime

from django.db.models import Q

from .models import Address, Coupon, CouponProgram, Order, OrderDetail, Partner, Product, ProductCategory

def get_or_none(classmodel, **kwargs):
  try:
    return classmodel.objects.get(**kwargs)
  except classmodel.DoesNotExist:
    return None

def get_product_categories_tree():
  categories = ProductCategory.objects.values()
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

def get_products_in_category(category_id):
  category = get_or_none(ProductCategory, id=category_id)
  if not category:
    return []
  category_childrens = category.get_childrens()
  category_children_ids = [i.id for i in category_childrens]
  products = Product.objects.filter(Q(category_id__in=category_children_ids) | Q(category_id=category_id))
  return products

def get_all_products():
  return Product.objects.all()

def get_product_by_id(product_id):
  return get_or_none(Product, pk=product_id)

def search_product(search_text):
  return Product.objects.filter(Q(name__icontains=search_text) | Q(slug__icontains=search_text))

def get_draft_order(**kwargs):
  return get_or_none(Order, **kwargs, status='draft')

def get_none_draft_orders(**kwargs):
  return Order.objects.filter(**kwargs).exclude(status='draft')

def get_available_coupon_programs():
  return CouponProgram.objects.filter(start_date__lte=datetime.today(), expired_date__gte=datetime.today())

def get_address_by_customer(customer):
  partner_orders = Order.objects.filter(customer=customer)
  address_ids = []
  for partner_order in partner_orders:
    address_ids.append(partner_order.shipping_address_id)
  return Address.objects.filter(pk__in=address_ids)

def get_coupon_by_order(order):
  return get_or_none(Coupon, order=order)

def get_coupon_by_code(code):
  return get_or_none(Coupon, code=code)

def get_partner_by_email(email):
  return get_or_none(Partner, email=email)

def get_base_context(request):
  context = {}
  if request.partner:
    user_email = request.partner.email
    context['order'] = get_draft_order(customer__email=user_email)
  context['product_categories'] = get_product_categories_tree()
  return context

def checkout(order, shipping_form, coupon_form):
  try:
    # Validate order here
    # Form after validating success
    # Save shipping information
    if coupon_form.cleaned_data['code']:
      coupon = get_coupon_by_code(coupon_form.cleaned_data['code'])
      if coupon:
        coupon.order = order
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
    order.receive_name = shipping_form.cleaned_data['receive_name']
    order.receive_phone = shipping_form.cleaned_data['receive_phone']
    order.receive_email = shipping_form.cleaned_data['receive_email']
    order.note = shipping_form.cleaned_data['note']
    order.shipping_address = address
    order.status = 'processing'
    order.calculate()
    order.save()
    # Update coupon program

    return True, None
  except Exception as e:
    return False, e

def sync_shopping_cart(email, shopping_cart):
  try:
    partner = get_or_none(Partner, email=email)
    order, is_new_order = Order.objects.get_or_create(customer=partner, status='draft')

    total = order.amount_sub_total
    for sp_orderdetail in shopping_cart['order']['orderdetails']:
      product = Product.objects.get(pk=sp_orderdetail['product']['id'])
      orderdetail, is_new_orderdetail = OrderDetail.objects.get_or_create(
        order=order,
        product=product,
        defaults={
          'quantity': sp_orderdetail['quantity'],
          'price_unit': product.price,
          'sub_price_unit': product.sub_price,
          'price_discount': sp_orderdetail['quantity'] * (product.price - product.sub_price),
          'amount_price': sp_orderdetail['quantity'] * product.price,
          'sub_total': sp_orderdetail['quantity'] * product.sub_price if product.sub_price else sp_orderdetail['quantity'] * product.price
        }
      )

      if not is_new_orderdetail:
        orderdetail.quantity += sp_orderdetail['quantity']
        orderdetail.amount_price = orderdetail.quantity * orderdetail.price_unit
        orderdetail.price_discount = orderdetail.quantity * (orderdetail.price_unit - orderdetail.sub_price_unit)
        orderdetail.sub_total = orderdetail.quantity * orderdetail.sub_price_unit if orderdetail.sub_price_unit else orderdetail.quantity * orderdetail.price_unit
        orderdetail.save()
      
      total += orderdetail.sub_total

    if (order.amount_sub_total != total):
      order.calculate()
      order.save()
    
    return True, partner, None
  except Exception as e:
    return False, None, e

def login_user(request, email):
  try:
    partner, is_new = Partner.objects.get_or_create(email=email)
    if is_new:
      partner.user = request.user
      partner.save()
    return True, partner, None
  except Exception as e:
    return False, None, e

def register(email, phone):
  try:
    partner = Partner.objects.create(
      email=email,
      phone=phone,
    )
    return True, partner, None
  except Exception as e:
    return False, None, e