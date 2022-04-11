from django.urls import path, include

from . import views


urlpatterns = [
  path('', views.index, name='index'),
  path('product-category/<int:category_id>', views.product_category, name='product_category'),
  path('product/<int:product_id>', views.product_detail, name='product_detail'),
  path('search/', views.search, name='search'),
  path('cart/', views.cart_detail, name='cart_detail'),
  path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
  path('accounts/', include('django.contrib.auth.urls')),
]

