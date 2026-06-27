from base64 import urlsafe_b64encode

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode

from accounts.forms import RegistrationForms
from accounts.models import Account


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
            return redirect("/account/login?command=varification&email="+email)
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
            auth.login(request, user)
            return redirect("home")
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

