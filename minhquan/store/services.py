from datetime import datetime

from django.db.models import Q

from .models import POS, Address, Coupon, CouponProgram, POSDetail, Partner, Product, ProductCategory

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

def get_draft_pos(**kwargs):
  return get_or_none(POS, **kwargs, status='draft')

def get_none_draft_poss(**kwargs):
  return POS.objects.filter(**kwargs).exclude(status='draft')

def get_available_coupon_programs():
  return CouponProgram.objects.filter(start_date__lte=datetime.today(), expired_date__gte=datetime.today())

def get_address_by_customer(customer):
  partner_poss = POS.objects.filter(customer=customer)
  address_ids = []
  for partner_pos in partner_poss:
    address_ids.append(partner_pos.shipping_address_id)
  return Address.objects.filter(pk__in=address_ids)

def get_coupon_by_pos(pos):
  return get_or_none(Coupon, pos=pos)

def get_coupon_by_code(code):
  return get_or_none(Coupon, code=code)

def get_partner_by_email(email):
  return get_or_none(Partner, email=email)

def get_base_context(request):
  context = {}
  if request.partner:
    user_email = request.partner.email
    context['pos'] = get_draft_pos(customer__email=user_email)
  context['product_categories'] = get_product_categories_tree()
  return context

def checkout(pos, shipping_form, coupon_form):
  try:
    # Validate pos here
    # Form after validating success
    # Save shipping information
    if coupon_form.cleaned_data['code']:
      coupon = get_coupon_by_code(coupon_form.cleaned_data['code'])
      if coupon:
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

    return True, None
  except Exception as e:
    return False, e

def sync_shopping_cart(email, shopping_cart):
  try:
    partner = get_or_none(Partner, email=email)
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