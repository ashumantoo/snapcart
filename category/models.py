from django.db import models

# Crategory Model
class Category(models.Model):
  category_name = models.CharField(max_length=50)
  slug = models.CharField(max_length=100)
  description = models.TextField(max_length=255, blank=True)
  cat_image = models.ImageField(upload_to='photos/categories', blank=True)
  
  
  class Meta:
    verbose_name_plural = 'categories'
    
  
  def __str__(self):
    return self.category_name