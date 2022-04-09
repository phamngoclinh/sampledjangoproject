from django.contrib import admin

from . import models


admin.site.register(models.Coupon)
admin.site.register(models.CouponProgram)
admin.site.register(models.Partner)
admin.site.register(models.UOMCategory)
admin.site.register(models.UOM)
admin.site.register(models.ProductCategory)
admin.site.register(models.Product)
admin.site.register(models.POS)
admin.site.register(models.POSDetail)

