from django.contrib import admin

from orders.models import Order, Payment, OrderProduct

#To display the Ordered Product inside the Order admin view in the form of table
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment','user','product','quantity','product_price','ordered')
    extra = 0 #By default Django add few rows to remove those rows use this

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number','full_name','email','phone','city','order_total','tax', 'status','is_ordered','created_at')
    list_filter = ('status','is_ordered')
    search_fields = ('order_number','first_name','last_name','phone','email')
    list_per_page = 20
    inlines = [OrderProductInline]

# Register your models here.
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)