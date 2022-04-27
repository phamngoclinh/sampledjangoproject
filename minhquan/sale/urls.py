from django.urls import path, include

from . import views


urlpatterns = [
  path('', views.index, name='index'),
  path('danh-sach-don-hang/', views.OrderListView.as_view(), name='order_list'),
  path('chien-luoc-san-pham/', views.program_list, name='program_list'),

  path('tao-don-hang/', views.OrderCreateView.as_view(), name='create_order'),
  path('sua-don-hang/<int:pk>', views.OrderUpdateView.as_view(), name='edit_order'),

  path('thanh-toan/<int:pk>', views.awaiting_payment, name='awaiting_payment'),
  path('thanh-toan-thanh-cong/<int:pk>', views.awaiting_fulfillment, name='awaiting_fulfillment'),
  path('shipper-nhan-hang/<int:pk>', views.awaiting_shipment, name='awaiting_shipment'),
  path('khach-nhan-hang/<int:pk>', views.awaiting_pickup, name='awaiting_pickup'),
  path('giao-hang-mot-phan/<int:pk>', views.partially_shipped, name='partially_shipped'),
  path('giao-hang-thanh-cong/<int:pk>', views.shipped, name='shipped'),
  path('hoan-tat-don-hang/<int:pk>', views.completed, name='completed'),
  path('huy-don-hang/<int:pk>', views.cancelled, name='cancelled'),
  path('tu-choi-don-hang/<int:pk>', views.declined, name='declined'),
  path('hoan-lai-mot-phan/<int:pk>', views.partially_refunded, name='partially_refunded'),
  path('hoan-lai-thanh-cong/<int:pk>', views.refunded, name='refunded'),
  path('tranh-chap/<int:pk>', views.disputed, name='disputed'),

  path('api/', include('sale.apis'))
]

