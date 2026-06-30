from base64 import urlsafe_b64encode
from multiprocessing import context

import requests
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.api import success
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode

from accounts.forms import RegistrationForms, UserForm, UserProfileForm
from accounts.models import Account, UserProfile
from carts.models import Cart, CartItem
from carts.views import _get_cart_id
from orders.models import Order, OrderProduct


def register(request):
    if request.method == "POST":
        form = RegistrationForms(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.phone_number = phone_number
            user.save()

            #create User Profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'avatars/avatar2.jpg'
            profile.save()

            #user activation
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_b64encode(force_bytes(user.pk)).decode(),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=(to_email,))
            send_email.send()

            # messages.success(request, "Thank you for registering with us. We have sent you a verifiction emaio to your email address. Please verify it.")
            return redirect("/accounts/login?command=varification&email="+email)
    else:
        form = RegistrationForms()

    context = {"form": form}
    return render(request, "register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                #If logged in user have item in cart then transfer the cart to the logged in user
                cart = Cart.objects.get(cart_id=_get_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    #getting the product variation by cart Id
                    product_variations = []
                    for item in cart_item:
                        variations = item.variations.all()
                        product_variations.append(list(variations))

                    #Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1,3,2,4,6]
                    # existing_variation_list = [4,6,2]
                    for pr in product_variations:
                        if pr in existing_variation_list:
                            index = existing_variation_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
            auth.login(request, user)
            messages.success(request,'You are now logged in')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print(query)
                #next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")

    return render(request, "login.html")


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'Your are logout.')
    return redirect('login')
    pass

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    user_profile = get_object_or_404(UserProfile, user=request.user)

    context = {
        'orders': orders,
        'orders_count': orders_count,
        'userprofile':user_profile
    }

    return render(request,'dashboard.html',context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_b64encode(force_bytes(user.pk)).decode(),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request,'Password reset email has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist.')
            return redirect('forgotPassword')
    return  render(request,'forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request,'Invalid link for resetting password')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            messages.error(request,'Password do not match')
            return redirect('resetPassword')
        else:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password) #set_password inbuilt function of django
            user.save()
            messages.success(request,'Password reset successful')
            return redirect('login')
    else:
        return render(request,'resetPassword.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)

    context = {
        'orders':orders
    }
    return render(request, 'my_orders.html',context)

@login_required(login_url='login')
def order_detail(request,order_number):
    order = Order.objects.get(order_number=order_number, is_ordered=True)
    order_products = OrderProduct.objects.filter(order_id=order.id)
    context = {
        'order':order,
        'order_detail': order_products
    }
    return render(request,'order_detail.html',context)

@login_required(login_url='login')
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated")
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
        context = {
            'user_form':user_form,
            'profile_form':profile_form,
            'userprofile': user_profile
        }
    return render(request,'edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        #check_password and set_password, django inbuilt function
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                #auth.logout(request)
                messages.success(request,'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request, "Please enter valid current password")
                return redirect('change_password')
        else:
            messages.error(request, "Confirm password did not match")
            return redirect('change_password')

    return render(request,'change_password.html')