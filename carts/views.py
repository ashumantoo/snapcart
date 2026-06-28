from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from carts.models import Cart, CartItem
from store.models import Product, Variation


# _ before the function make this as private function, getting the user session id from browser for guest user
def _get_cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)  # get the product
    #If user is authenticated
    if current_user.is_authenticated:
        product_variations = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variations.append(variation)
                except Exception as e:
                    print("Error: ", e)
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)
            if product_variations in existing_variation_list:
                # increase the cart quantity
                idx = existing_variation_list.index(product_variations)
                item_id = id[idx]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                # create a new cart item
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                # cart item variations
                if len(product_variations) > 0:
                    # if same variant is same for product then just update the quantity don't add the duplicate variant
                    item.variations.clear()
                    item.variations.add(
                        *product_variations
                    )
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)

            cart_item.save()
        return redirect("cart")

    #If user is not authenticated
    else:
        product_variations = []
        if request.method == "POST":
            # color = request.GET['color']
            # size = request.GET['size']

            # Instead of getting values from request one by one loop through through the request.POST
            # and get all the query paramas from the post method and extract the value accordingly
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value,
                    )
                    product_variations.append(variation)
                except Exception as e:
                    print("Error: ", e)
                    pass

        try:
            cart = Cart.objects.get(
                cart_id=_get_cart_id(request)
            )  # get the cart using the cart_id present in the user cokie session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_get_cart_id(request))
            cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing variation -> coming from DB
            # current variation -> product variation
            # item_id -> database
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)

            if product_variations in existing_variation_list:
                # increase the cart quantity
                idx = existing_variation_list.index(product_variations)
                item_id = id[idx]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                # creatre a new cart item
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                # cart item variations
                if len(product_variations) > 0:
                    # if same varant is same for product then just update the quantity don't add the duplicate variant
                    item.variations.clear()
                    item.variations.add(
                        *product_variations
                    )  # * will add all the variations
                # if item found in the cart just increase the quantity
                # cart_item.quantity += 1
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)
            cart_item.save()
        return redirect("cart")


def remove_from_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
      if request.user.is_authenticated:
          cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
      else:
          cart = Cart.objects.get(cart_id=_get_cart_id(request))
          cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
      if cart_item.quantity > 1:
          cart_item.quantity -= 1
          cart_item.save()
      else:
          cart_item.delete()
    except:
      pass
          
    return redirect("cart")


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    cart_item.delete()
    return redirect("cart")


def cart(request, total=0, quantity=0, cart_items=None):
    grand_total = 0
    tax = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "grand_total": grand_total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
    }
    return render(request, "cart.html", context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    grand_total = 0
    tax = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "grand_total": grand_total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
    }
    return render(request, 'checkout.html', context)