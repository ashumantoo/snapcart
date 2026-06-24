from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Account

class AccountAdmin(UserAdmin):
  list_display = ('email','first_name','last_name','username','last_login','date_joined','is_active')
  #makes column clickable
  list_display_links = ('email','first_name','last_name')
  readonly_fields = ('last_login','date_joined')
  ordering = ('-date_joined',)
  
  # this will make the password readonly
  filter_horizontal = ()
  list_filter = ()
  fieldsets = ()

# Register your models here.
admin.site.register(Account, AccountAdmin)