from datetime import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import *
from store.models import *
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.views.decorators.cache import cache_control, never_cache
import smtplib
import secrets
import re
from cart.cart import Cart
from django.conf import settings
import logging
logger = logging.getLogger(__name__)
from decimal import Decimal
import razorpay
from django.conf import settings
import time

razorpay_client = razorpay.Client(
    auth=("rzp_test_FIZcMWBmGnqoqG", "hwkP8FNx8gACO7YNZfQvUY1t")
)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def myaccount(request):
    if "email" in request.session:
        return redirect("home")
    main_category = Main_category.objects.all().order_by("-id")
    context = {"main_category": main_category}
    return render(request, "account/myaccount.html", context)


@never_cache
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        pass1 = request.POST.get("pass1")
        pass2 = request.POST.get("pass2")
        print(username, email, pass1, pass2)

        if not (username or email or mobile or pass1 or pass2):
            messages.error(request, "Please Fill Required Fields")
            return redirect("myaccount")
        
        if not is_valid_name(username):
            messages.error(request,"Please Enter Valid Name")
            return redirect("myaccount")
        
        if CustomUser.objects.filter(full_name=username):
            messages.error(request,"Username Already Taken")
            return redirect("myaccount")

        if not is_valid_password(pass1):
            messages.error(request,"Password Contain Atleast One capital,One special charactor,One Number and in Length of 8 characters")
            return redirect("myaccount")

        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return redirect("myaccount")

        if not validate_email(email):
            messages.error(request, "Please enter a valid email address")
            return redirect("myaccount")

        if not validate_number(mobile):
            messages.error(request, "Please enter a valid mobile number")
            return redirect("myaccount")

        if CustomUser.objects.filter(email=email):
            messages.error(request, "Email Already Taken")
            return redirect("myaccount")

        message,exp_time = generate_otp()
        sender_email = "vrsumindas007@gmail.com"
        receiver_mail = email
        password = "tmdw ctte rjef ruhe"

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_mail, message)
        except smtplib.SMTPAuthenticationError:
            messages.error(
                request,
                "Failed to send OTP email. Please check your email configuration.",
            )
            return redirect("register")

        user = CustomUser.objects.create_user(
            full_name=username, email=email, password=pass1, ph_no=mobile
        )
        UserWallet.objects.create(user=user)
        user.save()

        request.session["email"] = email
        request.session["otp"] = message
        request.session["exp_time"] = exp_time
        messages.success(request, "OTP is sent to your email")
        return redirect("verify_signup")

    return render(request, "account/myaccount.html")


def generate_otp(length=6, exp_time=60):
    current_time = int(time.time())
    exp_time = current_time + exp_time
    otp = "".join(secrets.choice("0123456789") for i in range(length))
    return otp, exp_time


def resend_otp(request):
    if request.method == "POST":
        email = request.session.get("email")
        if email:
            message, exp_time = generate_otp()
            sender_email = "vrsumindas007@gmail.com"
            receiver_mail = email
            password = "tmdw ctte rjef ruhe"

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_mail, message)
            except smtplib.SMTPAuthenticationError:
                messages.error(
                    request,
                    "Failed to send OTP email. Please check your email configuration.",
                )
                return redirect("register")

            request.session["otp"] = message
            request.session["exp_time"] = exp_time
            messages.success(request, "OTP is sent to your email")
            return redirect("verify_signup")
        else:
            print("Email not found in the session.")
    return redirect("register")


def validate_email(email):
    return "@" in email and "." in email


def validate_number(number):
    pattern = r"^\d{10}$"
    if re.match(pattern, number):
        return True
    else:
        return False


def is_valid_password(password):
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=!]).{8,}$"
    if re.match(pattern, password):
        return True
    else:
        return False


def is_valid_name(name):
    if not re.match("^[a-zA-Z]+$", name):
        return False
    if not 2 <= len(name) <= 50:
        return False
    return True

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def verify_signup(request):
    if request.method == "POST":
        user = CustomUser.objects.get(email=request.session["email"])
        x = request.session.get("otp")
        OTP = request.POST["otp"]
        otp_exp_time = request.session.get("exp_time")
        if int(time.time()) <= otp_exp_time:
            if OTP == x:
                user.is_verified = True
                user.save()
                del request.session["email"]
                del request.session["otp"]
                del request.session["exp_time"]
                auth.login(request, user)
                messages.success(request, "Signup successful!")
                device_id = request.COOKIES.get("device_id")
                response = redirect("verified_login")
                response.delete_cookie("device_id")
                return response
            else:
                user.delete()
                messages.info(request, "invalid otp")
                del request.session["email"]
                return redirect("verified_login")
        else:
            user.delete()
            messages.info(request, "OTP Has Expired")
            del request.session["email"]
            return redirect("verified_login")

    return render(request, "account/verify_otp.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def verified_login(request):
    main_category = Main_category.objects.all().order_by("-id")
    context = {"main_category": main_category}
    if "email" in request.session:
        return redirect("home")
    if request.method == "POST":
        username_email = request.POST.get("username")
        password = request.POST.get("password")
        print(username_email, password)
        user = authenticate(request, username=username_email, password=password)
        print(user)
        if user is not None:
            if not user.is_staff:
                cart_item_db = CartItem.objects.filter(user=user)
                cart = Cart(request)
                for cart_item in cart_item_db:
                    product = cart_item.product
                    quantity = cart_item.quantity
                    print(product, "---", quantity)
                    cart.add(product, quantity=quantity)
                cart_item_db.delete()
                auth.login(request, user)
                request.session["email"] = username_email
                return redirect("home")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("verified_login")
    return render(request, "account/login.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def logout(request):
    if "email" in request.session:
        cart_data = request.session.get(settings.CART_SESSION_ID, {})
        user = request.user
        for product_id, cart_item in cart_data.items():
            product = Product.objects.get(id=cart_item["product_id"])
            quantity = cart_item["quantity"]
            cart_item_db, created = CartItem.objects.get_or_create(
                user=user,
                product=product,
                quantity=quantity,
            )
            if not created:
                cart_item_db.quantity += quantity
                cart_item_db.save()
        request.session.flush()

    auth.logout(request)
    return redirect("home")


@login_required(login_url="verified_login")
def profile(request):
    user = request.user
    if not user.is_staff:
        main_category = Main_category.objects.all().order_by("-id")
        context = {"main_category": main_category}
    else:
        return redirect("verified_login")
    return render(request, "account/profile.html", context)


@login_required(login_url="verified_login")
def profile_update(request):
    # sourcery skip: none-compare, remove-redundant-if
    if request.method == "POST":
        full_name = request.POST.get("fullname")
        mobile = request.POST.get("phoneNo")
        email = request.POST.get("email")
        password = request.POST.get("currentPassword")
        user_id = request.user.id
        user = CustomUser.objects.get(id=user_id)
        user.full_name = full_name
        user.ph_no = mobile
        user.email = email
        if password == None and password != "":
            user.set_password = password
        user.save()

    return redirect("profile")


@login_required(login_url="verified_login")
def address(request):
    address_list = Address.objects.filter(user=request.user, is_deleted=False).order_by(
        "-id"
    )
    context = {
        "address_list": address_list,
    }
    return render(request, "account/address.html", context)


@login_required(login_url="verified_login")
def add_address(request):
    if request.method == "POST":
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        pincode = request.POST.get("pincode")

        new = Address.objects.create(
            user=request.user,
            first_name=fname,
            last_name=lname,
            email=email,
            number=phone,
            address=address,
            country=country,
            state=state,
            city=city,
            pin_code=pincode,
        )
        new.save()
        return redirect("address")

    return render(request, "account/add_address.html")


@login_required(login_url="verified_login")
def edit_address(request, id):
    user = request.user
    newaddress = Address.objects.get(id=id, user=user)
    context = {
        "newaddress": newaddress,
    }
    return render(request, "account/edit_address.html", context)


@login_required(login_url="verified_login")
def update_address(request, id):
    update = Address.objects.get(id=id, user=request.user)
    if request.method == "POST":
        update.first_name = request.POST.get("fname")
        update.last_name = request.POST.get("lname")
        update.email = request.POST.get("email")
        update.number = request.POST.get("phone")
        update.address = request.POST.get("address")
        update.country = request.POST.get("country")
        update.state = request.POST.get("state")
        update.city = request.POST.get("city")
        update.pin_code = request.POST.get("pincode")

        update.save()

        return redirect("address")


@login_required(login_url="verified_login")
def delete_address(request, id):
    try:
        address = Address.objects.get(id=id)
        address.is_deleted = True
        address.save()
    except Address.DoesNotExist:
        return HttpResponse("Address Not Found")
    return redirect("address")


@login_required(login_url="verified_login")
@login_required(login_url="verified_login")
def place_order(request):
    action = request.POST.get("action")
    print(action)
    if request.method == "POST" and action == "add_address":
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        pincode = request.POST.get("pincode")

        new = Address.objects.create(
            user=request.user,
            first_name=fname,
            last_name=lname,
            email=email,
            number=phone,
            address=address,
            country=country,
            state=state,
            city=city,
            pin_code=pincode,
        )
        new.save()
        return redirect("checkout")
    discount = None
    user = request.user
    cart_item = request.session.get(settings.CART_SESSION_ID, {})
    tax = sum(i["tax"] for i in cart_item.values() if i)
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        address_id = request.POST.get("billing_address")
        applied_coupon = request.POST.get("coupon_code")
        applied_category_offer = request.POST.get("category_offer")
        print("Payment Method:", payment_method)
        print("Address ID:", address_id)
        print("Coupon_price:", applied_coupon)
        print("Category_code:", applied_category_offer)
        if not address_id:
            return HttpResponse("Please Add an address")
        total_quantity = sum(item["quantity"] for item in cart_item.values())
        total_price = sum(
            item["price"] * item["quantity"] for item in cart_item.values()
        )
        total_price = total_price + tax
        if total_price < 300:
            total_price += 40
        print(total_price, "--no-discount--")
        if applied_coupon:
            try:
                discount = Coupon.objects.get(code=applied_coupon)
            except Coupon.DoesNotExist:
                return HttpResponse("Invalid coupon code")
            coupon = get_object_or_404(Coupon, code=applied_coupon)
            user_coupon_usage, created = UserCouponUsage.objects.get_or_create(
                user=request.user, coupon=coupon
            )
            if user_coupon_usage.used:
                return HttpResponse("You have already used this coupon.")
            discount_value = float(discount.discount)
            user_coupon_usage.used = True
            user_coupon_usage.save()
            print(discount_value)
            total_price = float(total_price)
            total_price_dis = total_price - (total_price * discount_value / 100)
            total_price = total_price_dis
            request.session["total_price_dis"] = total_price_dis
        print(total_price, "*****")
        if applied_category_offer:
            try:
                offer = Offer.objects.get(id=applied_category_offer)
            except Offer.DoesNotExist:
                return HttpResponse("Invalid offer code")
            offer_value = float(offer.discount)
            total_price = float(total_price)
            total_price_offer = total_price - (total_price * offer_value / 100)
            total_price = total_price_offer
        print(total_price, "--offer---")
        order = Order.objects.create(
            user=user,
            address_id=address_id,
            payment_type=payment_method,
            amount=total_price,
            quantity=total_quantity,
        )

        order.save()
        request.session["order_id"] = order.id
        if payment_method == "Pay with Razorpay":
            client = razorpay.Client(
                auth=("rzp_test_FIZcMWBmGnqoqG", "hwkP8FNx8gACO7YNZfQvUY1t")
            )
            order_amount = int(total_price * 100)
            currency = "INR"
            request.session["razorpay_amount"] = order_amount
            razorpay_order = client.order.create(
                {
                    "amount": order_amount,
                    "currency": currency,
                    "payment_capture": 1,
                }
            )
            request.session["razorpay_order_id"] = razorpay_order["id"]
            return redirect("razorpay_payment")

        for product_id, item in cart_item.items():
            product = Product.objects.get(id=product_id)
            order_item = OrderItem(
                order=order,
                product=product,
                quantity=item["quantity"],
                image=item["featured_image"],
            )
            order_item.save()
            product.total_quantity -= 1
            product.save()

    request.session["cart"] = {}
    return redirect("order_success")


def razorpay_payment(request):
    order_id = request.session.get("razorpay_order_id")
    request.session["cart"] = {}
    return render(request, "Main/razorpay.html", {"order_id": order_id})


def order_success(request):
    return render(request, "Main/order_success.html")


def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")
    return render(request, "account/order_list.html", {"orders": orders})


def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    orderAddress = OrderAddress.objects.filter(order=order)
    return render(
        request,
        "account/order_details.html",
        {"order": order, "address": address, "orderAddress": orderAddress},
    )


def order_cancel(request, id):
    order = Order.objects.get(id=id)
    if order.user == request.user:
        order.status = "Canceled"
        order.save()
        return redirect("orders_list")
    else:
        return HttpResponse("User Not Found")


def return_order(request, order_id):
    # sourcery skip: extract-duplicate-method, hoist-statement-from-if
    user = request.user
    usercustm = CustomUser.objects.get(email=user)
    order = Order.objects.get(id=order_id)
    if order.status == "completed" and order.payment_type == "cash_on_delivery":
        wallet_transaction = WalletTransaction.objects.create(
            wallet=usercustm.userwallet,
            description=f"Refund for Order #{order.id}",
            amount=order.amount,
        )
        wallet_transaction.save()
        order.amount = Decimal(order.amount)
        usercustm.wallet_bal += order.amount
        order.status = "refunded"
        order.save()
        return redirect("orders_list")
    elif order.payment_type == "Pay with Razorpay":
        wallet_transaction = WalletTransaction.objects.create(
            wallet=usercustm.userwallet,
            description=f"Refund for Order #{order.id}",
            amount=order.amount,
        )
        order.amount = Decimal(order.amount)
        usercustm.wallet_bal += order.amount
        usercustm.save()
        order.status = "refunded"
        order.save()
        return redirect("orders_list")
    elif order.status == "cancelled" and order.payment_type == "cash_on_delivery":
        wallet_transaction = WalletTransaction.objects.create(
            wallet=usercustm.userwallet,
            description=f"Refund for Order #{order.id}",
            amount=order.amount,
        )
        wallet_transaction.save()
        order.amount = Decimal(order.amount)
        usercustm.wallet_bal += order.amount
        order.status = "refunded"
        order.save()
        return redirect("orders_list")
    else:
        order.status = "Canceled"
        order.save()
        return redirect("orders_list")


@login_required(login_url="verified_login")
def wallet(request):
    user = request.user
    usercustm = CustomUser.objects.get(email=user)
    try:
        wallet = UserWallet.objects.get(user=usercustm)
        transactions = WalletTransaction.objects.filter(wallet=wallet).order_by(
            "-timestamp"
        )
        context = {
            "wallet": wallet,
            "transactions": transactions,
        }
    except UserWallet.DoesNotExist:
        context = {
            "wallet": 0,
        }

    return render(request, "account/wallet.html", context)

@login_required(login_url="verified_login")
def wishlist(request):
    user = request.user
    wish = WishList.objects.filter(user=user)
    return render(request, "Main/wishlist.html", {"wish": wish})


def add_to_wish(request, id):
    product = Product.objects.get(id=id)
    user = request.user
    wishlist, created = WishList.objects.get_or_create(product=product, user=user)
    wishlist.save()
    return redirect("wishlist")


def remove_from_wishlist(request, id):
    product = Product.objects.get(id=id)
    if request.user.is_authenticated:
        wish = WishList.objects.get(product=product, user=request.user)
    else:
        wish = WishList.object.get(product=product)
    wish.delete()
    return redirect("wishlist")


from io import BytesIO


def generate_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    print(order_items)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Add a border to the page
    width, height = letter
    p.rect(10, 10, width - 20, height - 20)

    p.drawString(100, 750, f"Invoice for Order #{order_id}")
    p.drawString(100, 720, f"User: {order.user}")
    p.drawString(100, 700, f"Address: {order.address}")
    # Initialize y_position
    y_position = 650

    # Split the address into multiple lines

    total_amount = 0  # Initialize total amount

    for item in order_items:
        p.drawString(100, y_position, f"Product: {item.product}")
        p.drawString(100, y_position - 20, f"Quantity: {item.quantity}")
        item_total = item.product.price * item.quantity
        p.drawString(100, y_position - 40, f"Price: {item_total}")
        total_amount += item_total
        y_position -= 60

    p.drawString(100, y_position - 20, f"Total Amount: {total_amount}")
    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice-{order_id}.pdf'
    return response
