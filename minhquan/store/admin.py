from django.contrib import admin

from .models import Coupon, CouponProgram, Partner, POS, POSDetail, ProductCategory, Product, UOM, UOMCategory


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


class POSDetailInline(admin.TabularInline):
  model = POSDetail
  extra = 3


class POSAdmin(admin.ModelAdmin):
  inlines = [POSDetailInline]


admin.site.register(CouponProgram, CouponProgramAdmin)
admin.site.register(Coupon)
admin.site.register(Partner)
admin.site.register(UOMCategory, UOMCategoryAdmin)
admin.site.register(UOM)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(POS, POSAdmin)
admin.site.register(POSDetail)

