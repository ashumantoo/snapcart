from ast import If

from django.conf.locale import ca
from django.db.models import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render

from carts.apps import CartsConfig
from carts.models import Cart, CartItem
from store.models import Product

# Create your views here.

#_ before the funtion make this as private function, getting the user session id from brower for guest user
def _get_cart_id(request):
  cart_id = request.session.session_key
  if not cart_id:
    cart_id = request.session.create()  
  return cart_id

def add_to_cart(request,product_id):
  product = Product.objects.get(id=product_id) #get the product
  
  try:
    cart = Cart.objects.get(cart_id=_get_cart_id(request)) #get the cart using the cart_id present in the user cokie session
  except Cart.DoesNotExist:
    cart = Cart.objects.create(
      cart_id= _get_cart_id(request)
    )
    cart.save()
  
  try:
    cart_item = CartItem.objects.get(product=product,cart=cart)
    #if item found in the cart just increase the quantity
    cart_item.quantity += 1
    cart_item.save()
    
  except CartItem.DoesNotExist:
    cart_item = CartItem.objects.create(
      product=product,
      quantity=1,
      cart=cart,
    )  
    cart_item.save()
  return redirect('cart')

def remove_from_cart(request,product_id):
  cart = Cart.objects.get(cart_id=_get_cart_id(request))
  product = get_object_or_404(Product,id=product_id)
  cart_item = CartItem.objects.get(product=product, cart=cart)
  if cart_item.quantity > 1:
    cart_item.quantity -= 1
    cart_item.save()
  else:
    cart_item.delete()
  return redirect('cart')


def remove_cart_item(request,product_id):
  cart = Cart.objects.get(cart_id=_get_cart_id(request))
  product = get_object_or_404(Product,id=product_id)
  cart_item = CartItem.objects.get(cart=cart,product=product)
  cart_item.delete()
  return redirect('cart')
  
def cart(request, total=0, quantity=0, cart_items=None):
  try:
    cart = Cart.objects.get(cart_id=_get_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    for item in cart_items:
      total += (item.product.price * item.quantity)
      quantity += item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
  except ObjectDoesNotExist:
    pass
  
  context = {
    'total':total,
    'grand_total': grand_total,
    'quantity':quantity,
    'cart_items':cart_items,
    'tax': tax
  }    
    
  return render(request,'cart.html',context)