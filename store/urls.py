from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from snapcart.settings import MEDIA_ROOT
from store import views

urlpatterns = [
    path("", views.store, name="store"),
    path("<slug:category_slug>", views.store, name="products_by_category"),
]
