import random
import re
import os
from datetime import datetime, timedelta

from django.db.models import Q
from django.core import mail
from django.template.loader import render_to_string, get_template

from .models import Address, Coupon, CouponProgram, Order, OrderDeliver, OrderDetail, Partner, Product, ProductCategory

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

def get_products_in_category(slug):
  category = get_or_none(ProductCategory, slug=slug)
  if not category:
    return [], None
  category_childrens = category.get_childrens()
  category_children_ids = [i.id for i in category_childrens]
  products = Product.objects.filter(Q(category_id__in=category_children_ids) | Q(category_id=category.id))
  return products, category

def get_group_products(category_slug=None):
  if not category_slug:
    root_categories = ProductCategory.objects.filter(parent_id__isnull=True)
  else:
    root_categories = ProductCategory.objects.filter(slug=category_slug)
  products = []
  for root_category in root_categories:
    _products, c = get_products_in_category(root_category.slug)
    product_category = {
      'category': root_category,
      'categories': root_category.get_childrens(),
      'products': _products
    }
    products.append(product_category)
  return products

def get_all_products():
  return Product.objects.all()

def get_product_by_id(product_id):
  return get_or_none(Product, pk=product_id)

def get_product_by_slug(product_slug):
  return get_or_none(Product, slug=product_slug)

def search_product(search_text, **kwargs):
  return Product.objects.filter(Q(**kwargs), Q(name__icontains=search_text) | Q(slug__icontains=search_text))

def get_order_by_id(order_id, **kwargs):
  return get_or_none(Order, **kwargs, pk=order_id)

def get_draft_order(**kwargs):
  return get_or_none(Order, **kwargs, orderdeliver__status='draft')

def get_draft_orders(**kwargs):
  return Order.objects.filter(**kwargs, orderdeliver__status='draft')

def get_incomming_orders(**kwargs):
  return Order.objects.filter(
    Q(**kwargs) &
    (Q(orderdeliver__status='draft') | Q(orderdeliver__status='confirmed'))
  )

def get_incomming_orders_exclude_user(user, **kwargs):
  return Order.objects.filter(
    ~Q(created_user=user) &
    Q(**kwargs) &
    (Q(orderdeliver__status='draft') | Q(orderdeliver__status='confirmed'))
  )

def get_none_draft_orders(**kwargs):
  return Order.objects.filter(**kwargs).exclude(orderdeliver__status='draft')

def get_partner_order_by_id(order_id, partner):
  order = get_or_none(Order, pk=order_id)
  if not order:
    return None
  if order.customer != partner:
    return None
  return order

def get_user_orders(user):
  orders = Order.objects.filter(created_user=user)
  return orders

def get_order_delivers_by_order(order, **kwargs):
  return OrderDeliver.objects.filter(**kwargs, order=order)

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

def search_partner(search_text):
  return Partner.objects.filter(
    Q(email__icontains=search_text) |
    Q(full_name__icontains=search_text) |
    Q(first_name__icontains=search_text) |
    Q(last_name__icontains=search_text) |
    Q(phone__icontains=search_text)
  )

def search_address(search_text):
  return Address.objects.filter(
    Q(city__icontains=search_text) |
    Q(district__icontains=search_text) |
    Q(award__icontains=search_text) |
    Q(address__icontains=search_text)
  )

def search_address_by_partner(search_text, partner):
  addresses = get_address_by_customer(partner)
  return addresses.filter(
    Q(city__icontains=search_text) |
    Q(district__icontains=search_text) |
    Q(award__icontains=search_text) |
    Q(address__icontains=search_text)
  )

def get_base_context(request):
  context = {}
  if request.partner:
    user_email = request.partner.email
    context['shopping_cart'] = get_draft_orders(customer__email=user_email).first()
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
    order.complete_deliver()
    order.save()
    # Update coupon program

    return True, None
  except Exception as e:
    return False, e

def sync_shopping_cart(email, shopping_cart):
  try:
    partner = get_or_none(Partner, email=email)
    order = get_draft_order(customer=partner)
    if not order:
      order = Order.objects.create(customer=partner)
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

def generate_otp(request):
  try:
    # Send OTP to Email
    # TODO Send OTP to MobilePhone
    otp_code = random.randint(100000,999999)
    send_email_status = 0
    a = os.environ
    with mail.get_connection() as connection:
      ctx = {
        'otp_code': otp_code
      }
      message = get_template('store/email/otp_email.html').render(ctx)
      subject_pattern = r'<title>(.+\w)<\/title>'
      subject = re.search(subject_pattern, message)

      email = mail.EmailMessage(
        subject and subject.group(1) or '',
        message,
        to=[request.POST.get('email') or request.session.get('login_form_email')],
        connection=connection,
      )
      email.content_subtype = "html"
      send_email_status = email.send()
    
    if send_email_status:
      request.session['otp_code'] = otp_code
      request.session['otp_expired'] = (datetime.today() + timedelta(seconds=60)).timestamp()
      return True

    return False
  except Exception as e:
    return False

def validate_otp(request, code):
  return code == str(request.session.get('otp_code')) and request.session.get('otp_expired') > (datetime.today()).timestamp()

def save_temporary_login_form(request, form):
  request.session['login_form_email'] = form.cleaned_data['email']
  request.session['login_form_shopping_cart'] = form.cleaned_data['shopping_cart']

def clear_temporary_data_after_login(request):
  request.session.__delitem__('otp_code')
  request.session.__delitem__('otp_expired')
  request.session.__delitem__('login_form_email')
  request.session.__delitem__('login_form_shopping_cart')