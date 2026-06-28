import datetime

from django.contrib import messages
from django.core.mail import message
from django.http import HttpResponse
from django.shortcuts import render, redirect

from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, Payment


def payments(request, order_number):
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
    prefix = 'TXN'
    date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S") #20260628124530
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
    messages.success(request, 'Order place successfully')
    return redirect('dashboard')


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
    return HttpResponse("Order complete")
