from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from .models import CouponProgram, Order, Partner, Product

from .forms import CouponProgramModelForm, OrderDetailInlineFormSet, OrderModelForm

from . import services


def index(request):
  return render(request, 'sale/index.html', {
    'title': 'Sale Management'
  })

class OrderListView(ListView):
  model = Order
  paginate_by = 100
  template_name = 'sale/order-list.html'

  def get_queryset(self, **kwargs):
    # qs = super().get_queryset(**kwargs)
    return services.get_user_joining_orders(self.request.user)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = 'Danh sách đơn hàng'
    context['incomming_orders'] = services.get_incomming_orders_exclude_user(self.request.user)
    return context


class OrderCreateView(CreateView):
  model = Order
  template_name = 'sale/create-order.html'
  fields = ['customer', 'receive_name', 'receive_phone', 'receive_email', 'shipping_address', 'note']
  success_url = reverse_lazy('order_list')

  def form_valid(self, form):
    ctx = self.get_context_data()
    inlines = ctx['inlines']
    if inlines.is_valid() and form.is_valid():
      order = form.save(commit=False)
      order.created_user = self.request.user
      order.save()
      inlines.instance = order
      inlines.save()
      return super().form_valid(form)
    else:
      return self.form_invalid(form)
  
  # We populate the context with the forms. Here I'm sending
  # the inline forms in `inlines`
  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx['title'] = 'Tạo đơn hàng'
    if self.request.POST:
      ctx['form'] = OrderModelForm(self.request.POST, instance=self.object)
      ctx['inlines'] = OrderDetailInlineFormSet(self.request.POST, instance=self.object)
    else:
      ctx['form'] = OrderModelForm(instance=self.object)
      ctx['inlines'] = OrderDetailInlineFormSet(instance=self.object)
    return ctx

class OrderUpdateView(UpdateView):
  model = Order
  template_name = 'sale/edit-order.html'
  fields = ['customer', 'receive_name', 'receive_phone', 'receive_email', 'shipping_address', 'note']
  success_url = reverse_lazy('order_list')

  def form_valid(self, form):
    ctx = self.get_context_data()
    inlines = ctx['inlines']
    if inlines.is_valid() and form.is_valid():
      inlines.save()
      order = form.save(commit=False)
      order.save()
      return super().form_valid(form)
    else:
      return self.form_invalid(form)
  
  # We populate the context with the forms. Here I'm sending
  # the inline forms in `inlines`
  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx['title'] = 'Sửa đơn hàng'
    if self.request.POST:
      ctx['form'] = OrderModelForm(self.request.POST, instance=self.object)
      ctx['inlines'] = OrderDetailInlineFormSet(self.request.POST, instance=self.object)
    else:
      ctx['form'] = OrderModelForm(instance=self.object)
      ctx['inlines'] = OrderDetailInlineFormSet(instance=self.object)
      ctx['order'] = self.object
    return ctx


class CouponProgramListView(ListView):
  model = CouponProgram
  paginate_by = 100
  template_name = 'sale/couponprogram/couponprogram-list.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = 'Danh sách khuyến mãi'
    return context


class CouponProgramCreateView(CreateView):
  model = CouponProgram
  form_class = CouponProgramModelForm
  template_name = 'sale/couponprogram/create-couponprogram.html'
  success_url = reverse_lazy('program_list')

  def form_valid(self, form):
    if form.is_valid():
      return super().form_valid(form)
    else:
      return self.form_invalid(form)
  
  # We populate the context with the forms. Here I'm sending
  # the inline forms in `inlines`
  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx['title'] = 'Tạo chương trình'
    ctx['sale_product_categories'] = services.get_all_product_category()

    if self.request.POST:
      ctx['form'] = CouponProgramModelForm(self.request.POST, instance=self.object)
    else:
      ctx['form'] = CouponProgramModelForm(instance=self.object)

    return ctx


class CouponProgramUpdateView(UpdateView):
  model = CouponProgram
  form_class = CouponProgramModelForm
  template_name = 'sale/couponprogram/edit-couponprogram.html'

  def get_success_url(self):
    return reverse_lazy('edit_couponprogram', kwargs={'pk': self.object.id})
  
  def form_valid(self, form):
    if form.is_valid():
      new_couponprogram = form.save(commit=False)
      json_q = services.make_rule_json_as_queryable(form.cleaned_data['rule_product'])
      new_couponprogram.products.set(services.filter_model_by_q(json_q, Product))
      new_couponprogram.save()
      form.save_m2m()
      return super().form_valid(form)
    return self.form_invalid(form)
  
  # We populate the context with the forms. Here I'm sending
  # the inline forms in `inlines`
  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx['title'] = 'Cập nhật chương trình'
    ctx['sale_product_categories'] = services.get_all_product_category()

    if self.object.rule_product:
      products_filterable = services.make_rule_json_as_queryable(self.object.rule_product)
      products = services.execute_json_rule(products_filterable, Product)
      ctx['rule_product_mapping_result'] = products
    
    if self.object.rule_customer:
      customers_filterable = services.make_rule_json_as_queryable(self.object.rule_customer)
      customers = services.execute_json_rule(customers_filterable, Partner)
      ctx['rule_customer_mapping_result'] = customers
    
    if self.object.rule_order:
      orders_filterable = services.make_rule_json_as_queryable(self.object.rule_order)
      orders = services.execute_json_rule(orders_filterable, Order)
      ctx['rule_order_mapping_result'] = orders

    if self.request.POST:
      ctx['form'] = CouponProgramModelForm(self.request.POST, instance=self.object)
    else:
      ctx['form'] = CouponProgramModelForm(instance=self.object)
    
    return ctx


@login_required
def awaiting_payment(request, pk):
  order = services.get_order_by_id(pk)
  order.awaiting_payment(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def awaiting_fulfillment(request, pk):
  order = services.get_order_by_id(pk)
  order.awaiting_fulfillment(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def awaiting_shipment(request, pk):
  order = services.get_order_by_id(pk)
  order.awaiting_shipment(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def awaiting_pickup(request, pk):
  order = services.get_order_by_id(pk)
  order.awaiting_pickup(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def partially_shipped(request, pk):
  order = services.get_order_by_id(pk)
  order.partially_shipped(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def shipped(request, pk):
  order = services.get_order_by_id(pk)
  order.shipped(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def completed(request, pk):
  order = services.get_order_by_id(pk)
  order.completed(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def cancelled(request, pk):
  order = services.get_order_by_id(pk)
  order.cancelled(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def declined(request, pk):
  order = services.get_order_by_id(pk)
  order.declined(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def partially_refunded(request, pk):
  order = services.get_order_by_id(pk)
  order.partially_refunded(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def refunded(request, pk):
  order = services.get_order_by_id(pk)
  order.refunded(request.user)
  return redirect('edit_order', pk=pk)

@login_required
def disputed(request, pk):
  order = services.get_order_by_id(pk)
  order.disputed(request.user)
  return redirect('edit_order', pk=pk)
