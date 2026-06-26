from django.shortcuts import get_object_or_404, render

from carts.models import CartItem
from carts.views import _get_cart_id
from category.models import Category
from store.models import Product


# Create your views here.
def store(request, category_slug=None):
    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(is_available=True, category=category)

    else:
        products = Product.objects.all().filter(is_available=True)       
        
    product_count = products.count()
    context = {"products": products, "product_count": product_count}
    return render(request, "store.html", context)


def product_details(request,category_slug, product_slug):
    try:
        #__ is way to get access to property of foreign key Model
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_get_cart_id(request),product=product)
    
    except Exception as e:
        raise e    
    
    context = {
        'product': product,
        'in_cart': in_cart
    }
    return render(request, 'product-details.html', context)