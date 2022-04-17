from django.urls import path

from . import views


urlpatterns = [
  path('', views.index, name='index'),
  path('product-category/<int:category_id>', views.product_category, name='product_category'),
  path('product/<int:product_id>', views.product_detail, name='product_detail'),
  path('search/', views.search, name='search'),
  path('carts/', views.carts, name='carts'),
  path('cart/', views.cart, name='cart'),
  path('checkout/<int:pos_id>', views.checkout, name='checkout'),
  path('checkout-success/<int:pos_id>', views.checkout_success, name='checkout_success'),
  path('get-coupon/', views.get_coupon, name='get_coupon'),
  path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
  path('register/', views.register, name='register'),
  path('login/', views.login, name='login'),
  path('login-user/', views.login_user, name='login_user'),
  path('logout/', views.logout, name='logout'),
  path('profile/', views.profile, name='profile'),
]

