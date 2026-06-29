from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from carts.models import CartItem
from carts.views import _get_cart_id
from category.models import Category
from orders.models import OrderProduct
from store.forms import ReviewForm
from store.models import Product, ReviewRating


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

    try:
        order_product = OrderProduct.objects.filter(user=request.user.id, product_id=product.id).exists()
    except OrderProduct.DoesNotExist:
        order_product = None

    #Get the reviews
    reviews = ReviewRating.objects.filter(product_id=product.id,status=True)

    context = {
        "product": product,
        "in_cart": in_cart,
        'orderProduct': order_product,
        'reviews': reviews,
    }
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


def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER') #This will give the prv page url
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user_id=request.user, product__id=product_id)
            #by passing review as instance we are telling django to update the review if exists instead of
            # creating a new - This approach we should take generally when we want to do a update on any model
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request,'Thank you! your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request,'Thank you! your review has been submitted.')
                return redirect(url)

