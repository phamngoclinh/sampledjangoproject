from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .models import Order

from .forms import OrderDetailInlineFormSet, OrderModelForm

from . import services

@login_required
def order_list(request):
  context = {
    'title': 'Quản lý - Danh sách hóa đơn',
    'unprocessing_orders': services.get_unprocessing_orders(),
    'orders': services.get_user_orders(request.user)
  }
  return TemplateResponse(request, 'store/management/order-list.html', context)

# @login_required
class OrderCreateView(CreateView):
  model = Order
  template_name = 'store/management/create-order.html'
  fields = ['customer', 'receive_name', 'receive_phone', 'receive_email', 'shipping_address', 'note']
  success_url = reverse_lazy('order_list')

  def form_valid(self, form):
    form.instance.created_user = self.request.user
    return super().form_valid(form)
  
  # We populate the context with the forms. Here I'm sending
  # the inline forms in `inlines`
  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx['title'] = 'Quản lý - Tạo đơn hàng'
    if self.request.POST:
      ctx['form'] = OrderModelForm(self.request.POST)
      ctx['inlines'] = OrderDetailInlineFormSet(self.request.POST)
    else:
      ctx['form'] = OrderModelForm()
      ctx['inlines'] = OrderDetailInlineFormSet()
    return ctx


class OrderUpdateView(UpdateView):
  model = Order
  template_name = 'store/management/edit-order.html'
  fields = ['customer', 'receive_name', 'receive_phone', 'receive_email', 'shipping_address', 'note']
  success_url = reverse_lazy('order_list')

  def form_valid(self, form):
    ctx = self.get_context_data()
    inlines = ctx['inlines']
    if inlines.is_valid() and form.is_valid():
      inlines.save()
      self.object = form.save()
      return super().form_valid(form)
    else:
      return self.form_invalid(form)
  
  # We populate the context with the forms. Here I'm sending
  # the inline forms in `inlines`
  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx['title'] = 'Quản lý - Sửa đơn hàng'
    if self.request.POST:
      ctx['form'] = OrderModelForm(self.request.POST, instance=self.object)
      ctx['inlines'] = OrderDetailInlineFormSet(self.request.POST, instance=self.object)
    else:
      ctx['form'] = OrderModelForm(instance=self.object)
      ctx['inlines'] = OrderDetailInlineFormSet(instance=self.object)
    return ctx

@login_required
def edit_order(request, order_id):
  group_products = services.get_group_products(order_id)
  context = {
    'group_products': group_products,
    'title': 'Danh mục ' + group_products[0]['category'].name
  }
  return TemplateResponse(request, 'store/product_category.html', context)

def cancel_order(request, slug):
  product = services.get_product_by_slug(slug)
  context = {
    'product': product,
    'title': product.name
  }
  return TemplateResponse(request, 'store/product_detail.html', context)

@login_required
def create_partner(request):
  search_text = request.GET.get('tu-khoa', '')
  context = {
    'products': services.search_product(search_text),
    'title': 'Tìm kiếm từ khóa ' + search_text
  }
  return TemplateResponse(request, 'store/search.html', context)

@login_required
def confirm_order(request):
  search_text = request.GET.get('tu-khoa', '')
  context = {
    'products': services.search_product(search_text),
    'title': 'Tìm kiếm từ khóa ' + search_text
  }
  return TemplateResponse(request, 'store/search.html', context)


urlpatterns = [
  path('danh-sach-don-hang/', order_list, name='order_list'),
  path('tao-don-hang/', OrderCreateView.as_view(), name='create_order'),
  path('sua-don-hang/<int:pk>', OrderUpdateView.as_view(), name='edit_order'),
  path('xac-nhan-don-hang/<int:pk>', confirm_order, name='confirm_order'),
  path('huy-don-hang/', cancel_order, name='cancel_order'),
  path('tao-khach-hang/', create_partner, name='create_partner'),
]