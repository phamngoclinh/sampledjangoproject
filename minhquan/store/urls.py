from django.urls import path, include

from . import views


urlpatterns = [
  path('', views.index, name='index'),
  path('product-category/<int:category_id>', views.product_category, name='product_category'),
  path('product/<int:product_id>', views.product_detail, name='product_detail'),
  path('cart/', views.cart_detail, name='cart_detail'),
  path('accounts/', include('django.contrib.auth.urls')),
]

