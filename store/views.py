from ast import If

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from carts.models import CartItem
from carts.views import _get_cart_id
from category.models import Category
from store.models import Product


# Create your views here.
def store(request, category_slug=None):
    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = (
            Product.objects.all()
            .filter(is_available=True, category=category)
            .order_by("id")
        )
        paginator = Paginator(products, 1)
        page = request.GET.get(
            "page"
        )  # This we will get from frontend with the url like 'example.com/store/page=1'
        paged_products = paginator.get_page(page)

    else:
        products = Product.objects.all().filter(is_available=True).order_by("id")
        paginator = Paginator(products, 3)
        page = request.GET.get(
            "page"
        )  # This we will get from frontend with the url like 'example.com/store/page=1'
        paged_products = paginator.get_page(page)

    product_count = products.count()
    context = {"products": paged_products, "product_count": product_count}
    return render(request, "store.html", context)


def product_details(request, category_slug, product_slug):
    try:
        # __ is way to get access to property of foreign key Model
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(
            cart__cart_id=_get_cart_id(request), product=product
        )

    except Exception as e:
        raise e

    context = {"product": product, "in_cart": in_cart}
    return render(request, "product-details.html", context)


def search(request):
    if "keyword" in request.GET:
        search_keyword = request.GET["keyword"]
        if search_keyword:
            # icontains = It will match the keyword with the description
            # Q - to query the complex query over the data
            # 👇🏽simple filter query with single parameter
            # products = Product.objects.order_by('-created_date').filter(description__icontains=search_keyword)

            # 👇🏽complex filter query over multiple parameter, need to use Q
            products = Product.objects.order_by("-created_date").filter(
                Q(description__icontains=search_keyword)
                | Q(product_name__icontains=search_keyword)
            )
            product_count = products.count()
    context = {"products": products, "product_count": product_count}
    return render(request, "store.html", context)
