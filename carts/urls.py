from django.urls import path

from carts import views
from snapcart.settings import MEDIA_ROOT

urlpatterns = [
    path("", views.cart, name="cart"),
    path("add_to_cart/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    # path("place_order/", views.place_order, name="place_order"),
    path("remove_from_cart/<int:product_id>/<int:cart_item_id>", views.remove_from_cart, name="remove_from_cart"),
    path("remove_cart_item/<int:product_id>/<int:cart_item_id>", views.remove_cart_item, name="remove_cart_item")
]
