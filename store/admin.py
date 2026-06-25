from django.contrib import admin
from django.contrib.admin.templatetags.admin_modify import prepopulated_fields_js

from store.models import Product


class ProductAdmin(admin.ModelAdmin):
  list_display = ('product_name','price','stock','category','updated_date','is_available')
  prepopulated_fields = {'slug':('product_name',)}
  

# Register your models here.
admin.site.register(Product, ProductAdmin)