from django.contrib import admin

from .models import Address, Coupon, CouponProgram, OrderDeliver, Partner, Order, OrderDetail, ProductCategory, Product, UOM, UOMCategory


class CouponInline(admin.TabularInline):
  model = Coupon
  extra = 3


class CouponProgramAdmin(admin.ModelAdmin):
  inlines = [CouponInline]


class UOMInline(admin.TabularInline):
  model = UOM
  extra = 3


class UOMCategoryAdmin(admin.ModelAdmin):
  inlines = [UOMInline]


class OrderDetailInline(admin.TabularInline):
  model = OrderDetail
  extra = 3


class OrderDeliverInline(admin.TabularInline):
  model = OrderDeliver
  extra = 0


class OrderAdmin(admin.ModelAdmin):
  inlines = [OrderDetailInline, OrderDeliverInline]


admin.site.register(CouponProgram, CouponProgramAdmin)
admin.site.register(Coupon)
admin.site.register(Partner)
admin.site.register(UOMCategory, UOMCategoryAdmin)
admin.site.register(UOM)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(OrderDeliver)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail)
admin.site.register(Address)

