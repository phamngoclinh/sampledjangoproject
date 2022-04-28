from django.contrib import admin

from . import models


class CouponInline(admin.TabularInline):
  model = models.Coupon
  extra = 3


class CouponProgramAdmin(admin.ModelAdmin):
  inlines = [CouponInline]


class UOMInline(admin.TabularInline):
  model = models.UOM
  extra = 3


class UOMCategoryAdmin(admin.ModelAdmin):
  inlines = [UOMInline]


class OrderDetailInline(admin.TabularInline):
  model = models.OrderDetail
  extra = 3


class OrderDeliverInline(admin.TabularInline):
  model = models.OrderDeliver
  extra = 0


class OrderAdmin(admin.ModelAdmin):
  inlines = [OrderDetailInline, OrderDeliverInline]


admin.site.register(models.CouponProgram, CouponProgramAdmin)
admin.site.register(models.Coupon)
admin.site.register(models.Partner)
admin.site.register(models.UOMCategory, UOMCategoryAdmin)
admin.site.register(models.UOM)
admin.site.register(models.ProductCategory)
admin.site.register(models.Product)
admin.site.register(models.OrderDeliver)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderDetail)
admin.site.register(models.Address)

