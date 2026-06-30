from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from accounts.models import Account, UserProfile


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

class UserProfileAdmin(admin.ModelAdmin):
  def thumbnail(self, obj):
    """Display profile picture thumbnail with error handling"""
    if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
      return format_html(
        '<img src="{}" width="30" height="30" style="border-radius:50%; object-fit:cover;">',
        obj.profile_picture.url
      )

    # Return default placeholder if no image
    return format_html(
      '<span style="display:inline-block; width:30px; height:30px; border-radius:50%; '
      'background:#ccc; text-align:center; line-height:30px; font-size:12px;">📷</span>'
    )
  thumbnail.short_description = 'Profile Picture'
  list_display = ('thumbnail', 'user', 'city', 'state', 'country')

# Register your models here.
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)