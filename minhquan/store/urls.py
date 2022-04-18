from django.urls import path, include

from . import views


urlpatterns = [
  path('', views.index, name='index'),
  path('product-category/<int:category_id>', views.product_category, name='product_category'),
  path('product/<int:product_id>', views.product_detail, name='product_detail'),
  path('search/', views.search, name='search'),
  path('orders/', views.orders, name='orders'),
  path('shopping-cart/', views.shopping_cart, name='shopping_cart'),
  path('checkout/<int:order_id>', views.checkout, name='checkout'),
  path('checkout-result/<int:order_id>', views.checkout_result, name='checkout_result'),
  path('register/', views.register, name='register'),
  path('login/', views.login, name='login'),
  path('login-user/', views.login_user, name='login_user'),
  path('logout/', views.logout, name='logout'),
  path('profile/', views.profile, name='profile'),
  path('api/', include('store.apis'))
]

