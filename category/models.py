from django.db import models
from django.urls import reverse

# Crategory Model
class Category(models.Model):
  category_name = models.CharField(max_length=50)
  slug = models.CharField(max_length=100)
  description = models.TextField(max_length=255, blank=True)
  cat_image = models.ImageField(upload_to='photos/categories', blank=True)
  
  
  class Meta:
    verbose_name_plural = 'categories'
    
    
  def get_url(self):
    # this will generate a url path for name='products_by_category' which is slug for category
    return reverse('products_by_category',args=[self.slug])
  
    
  def __str__(self):
    return self.category_name