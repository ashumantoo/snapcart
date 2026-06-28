import datetime
from urllib.parse import urlencode

from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderProduct
from store.models import Product


def payments(request, order_number):
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)

    prefix = 'TXN'
    date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 20260628124530
    payment_id = f"{prefix}-{date_str}"

    payment = Payment(
        user=request.user,
        payment_id=payment_id,
        payment_method="CASH",
        amount_paid=order.order_total,
        status="PAID",
    )
    payment.save()
    print("Payment created")
    order.payment = payment
    order.is_ordered = True
    order.save()
    print("Order updated with payment id")

    # Move the cart items to Order Product table
    cart_item = CartItem.objects.filter(user=request.user)
    for item in cart_item:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product.id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        # Since variations in OrderProduct model is many to many relation - We can not insert
        # variations value in the db before doing the save, We need to do that after initial save
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        # Reduce the quantity of the sold product i.e. decrease the stock
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity;
        product.save()

    # Clear the cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order received email to the customer
    mail_subject = "Thank you for your order."
    message = render_to_string('order_recieved_email.html', {
        'user': request.user,
        'order': order
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to user on thank you page
    base_url = reverse('order_complete')
    query_string = urlencode({
        'order_number': order.order_number,
        'payment_id': payment.payment_id
    })
    final_url = f"{base_url}?{query_string}"
    return redirect(final_url)


# Create your views here.
def place_order(request, total=0, quantity=0):
    current_user = request.user

    # if the cart count <= 0, then redirect back to shop
    cart_item = CartItem.objects.filter(user=current_user)
    cart_count = cart_item.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for item in cart_item:
        total += (item.product.price * item.quantity)
        quantity += item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            # store all the billing information inside order table
            data = Order()
            data.user = current_user
            data.first_name = order_form.cleaned_data['first_name']
            data.last_name = order_form.cleaned_data['last_name']
            data.phone = order_form.cleaned_data['phone']
            data.email = order_form.cleaned_data['email']
            data.address_line_1 = order_form.cleaned_data['address_line_1']
            data.address_line_2 = order_form.cleaned_data['address_line_2']
            data.country = order_form.cleaned_data['country']
            data.state = order_form.cleaned_data['state']
            data.city = order_form.cleaned_data['city']
            data.pincode = order_form.cleaned_data['pincode']
            data.order_note = order_form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')  # this will give the user ip
            data.save()

            # Generate the order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            # data.id, we will receive from the data since we have already save the data by data.save(
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_item,
                'total': total,
                'tax': tax,
                'grand_total': grand_total
            }
            return render(request, 'payments.html', context)
        else:
            return redirect('checkout')
    return None


def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=payment_id)

        sub_total = 0
        for i in order_products:
            sub_total += i.product.price * i.quantity

        context = {
            'order':order,
            'ordered_products':order_products,
            'order_number':order.order_number,
            'transID': payment.payment_id,
            'subtotal': sub_total
        }
        return render(request,'order_complete.html',context)
    except(Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')

