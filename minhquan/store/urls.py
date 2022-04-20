from django.urls import path, include

from . import views


urlpatterns = [
  path('', views.index, name='index'),
  path('danh-muc-san-pham/<slug:slug>', views.product_category, name='product_category'),
  path('san-pham/<slug:slug>', views.product_detail, name='product_detail'),
  path('tim-kiem/', views.search, name='search'),
  path('danh-sach-don-hang/', views.orders, name='orders'),
  path('don-hang/<int:order_id>', views.order, name='order'),
  path('gio-hang/', views.shopping_cart, name='shopping_cart'),
  path('thanh-toan/<int:order_id>', views.checkout, name='checkout'),
  path('ket-qua-thanh-toan/<int:order_id>', views.checkout_result, name='checkout_result'),
  path('dang-ky/', views.register, name='register'),
  path('dang-nhap/', views.login, name='login'),
  path('dang-nhap-he-thong/', views.login_user, name='login_user'),
  path('dang-nhap-otp/', views.login_otp, name='login_otp'),
  path('gui-lai-ma-otp/', views.resend_otp, name='resend_otp'),
  path('dang-xuat/', views.logout, name='logout'),
  path('thong-tin-ca-nhan/', views.profile, name='profile'),
  path('api/', include('store.apis'))
]

