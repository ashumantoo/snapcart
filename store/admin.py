from django.contrib import admin
from django.contrib.admin.templatetags.admin_modify import prepopulated_fields_js

from store.models import Product, Variation


class ProductAdmin(admin.ModelAdmin):
  list_display = ('product_name','price','stock','category','updated_date','is_available')
  prepopulated_fields = {'slug':('product_name',)}
  

class VariationAdmin(admin.ModelAdmin):
  list_display = ('product','variation_category','variation_value','is_active')  
  list_editable = ('is_active',)
  list_filter = (('product','variation_category','variation_value','is_active'))
  

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)