from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from .models import Order

from .forms import OrderDetailInlineFormSet, OrderModelForm

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
    context['title'] = 'Quản lý - Danh sách đơn hàng'
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
    ctx['title'] = 'Quản lý - Tạo đơn hàng'
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
    ctx['title'] = 'Quản lý - Sửa đơn hàng'
    if self.request.POST:
      ctx['form'] = OrderModelForm(self.request.POST, instance=self.object)
      ctx['inlines'] = OrderDetailInlineFormSet(self.request.POST, instance=self.object)
    else:
      ctx['form'] = OrderModelForm(instance=self.object)
      ctx['inlines'] = OrderDetailInlineFormSet(instance=self.object)
      ctx['order'] = self.object
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

@login_required
def program_list(request):
  return render(request, 'sale/program-list.html', {
    'title': 'Quản lý - Danh sách khuyến mãi'
  })


# urlpatterns = [
#   path('', index, name='management'),
#   path('danh-sach-don-hang/', OrderListView.as_view(), name='order_list'),
#   path('chien-luoc-san-pham/', program_list, name='program_list'),

#   path('tao-don-hang/', OrderCreateView.as_view(), name='create_order'),
#   path('sua-don-hang/<int:pk>', OrderUpdateView.as_view(), name='edit_order'),
  
#   path('khoi-tao-trang-thai/<int:pk>', init_order_status, name='init_order_status'),
#   path('xac-nhan-don-hang/<int:pk>', confirm_order, name='confirm_order'),
#   path('xu-ly-don-hang/<int:pk>', start_process_order, name='start_process_order'),
#   path('ket-thuc-xu-ly-don-hang/<int:pk>', finish_process_order, name='finish_process_order'),  
#   path('huy-don-hang/<int:pk>', cancel_order, name='cancel_order'),

#   path('thanh-toan/<int:pk>', awaiting_payment, name='awaiting_payment'),
#   path('thanh-toan-thanh-cong/<int:pk>', awaiting_fulfillment, name='awaiting_fulfillment'),
#   path('shipper-nhan-hang/<int:pk>', awaiting_shipment, name='awaiting_shipment'),
#   path('khach-nhan-hang/<int:pk>', awaiting_pickup, name='awaiting_pickup'),
#   path('giao-hang-mot-phan/<int:pk>', partially_shipped, name='partially_shipped'),
#   path('giao-hang-thanh-cong/<int:pk>', shipped, name='shipped'),
#   path('hoan-tat-don-hang/<int:pk>', completed, name='completed'),
# ]