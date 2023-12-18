from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse, HttpResponseForbidden
from store.models import *
from user.models import *
from django.contrib import messages, auth
from user.views import validate_email
from .forms import *
from django.contrib.auth import authenticate, logout
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.db.models import F
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.db.models import F, Q
from reportlab.lib import colors
from django.core.paginator import Paginator
from django.views.generic import ListView


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="admin_login")
def admin_base(request):
    return render(request, "admin-base.html")


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if "adminemail" in request.session:
        return redirect("index")
    elif request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not (email or password):
            messages.error(request, "Please Fill Required Fields")
            return redirect("admin_login")
        if not validate_email(email):
            messages.error(request, "Please Enter Valid Email")
            return redirect("admin_login")
        admin = authenticate(request, username=email, password=password)
        print(admin)
        if admin is not None and admin.is_staff:
            request.session["adminemail"] = email
            auth.login(request, admin)
            return redirect("index")
        else:
            messages.info(request, "invalid username or password")
            return redirect("admin_login")
    return render(request, "adminn/pages/authentication-login.html")


@user_passes_test(lambda u: u.is_staff, login_url="admin_login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def admin_logout(request):
    if "adminemail" in request.session:
        del request.session["adminemail"]
    logout(request)
    return redirect("admin_login")


@user_passes_test(lambda u: u.is_staff, login_url="admin_login")
@login_required(login_url="admin_login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def admin_index(request):
    total_users = CustomUser.objects.count()
    order_count = Order.objects.count()
    pending = Order.objects.filter(status="pending").count()
    total_revenue = 0
    for order in Order.objects.all():
        order_revenue = 0
        for order_item in order.orderitem_set.all():
            order_revenue += order_item.quantity * int(order_item.product.price)
        total_revenue += order_revenue
    monthly_order_counts = []
    for month in range(1, 13):
        count = Order.objects.filter(date__month=month).count()
        monthly_order_counts.append(count)
    context = {
        "total_users": total_users,
        "order_count": order_count,
        "total_revenue": total_revenue,
        "pending": pending,
        "monthly_order_counts": monthly_order_counts,
    }
    return render(request, "adminn/index.html", context)


def generate_pdf_sales_report(request):
    if request.method == "POST":
        start_date = request.POST.get("fromDate")
        end_date = request.POST.get("toDate")

        if not (start_date and end_date):
            return HttpResponse("Invalid Date Range")

        sales_data = Order.objects.filter(
            Q(status="completed") | Q(status="delivered"),
            date__gte=start_date,
            date__lte=end_date,
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="sales_report.pdf"'

        c = canvas.Canvas(response, pagesize=letter)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Sales Report")
        c.drawString(100, 720, f"Period: {start_date} - {end_date}")
        c.drawString(100, 700, "Sales Data")

        table_x = 100
        table_y = 680
        col_width = 100
        row_height = 20
        table_width = 400
        table_height = (len(sales_data) + 1) * row_height

        c.rect(table_x, table_y, table_width, -table_height, stroke=1, fill=0)

        col_x = table_x + col_width
        c.line(col_x, table_y, col_x, table_y - table_height)
        col_x += col_width
        c.line(col_x, table_y, col_x, table_y - table_height)

        c.setFillColor(colors.lightgrey)
        c.rect(table_x, table_y, table_width, -row_height, stroke=1, fill=1)
        c.setFillColorRGB(0, 0, 0)

        c.drawString(table_x + 10, table_y - 10, "Order ID")
        c.drawString(table_x + col_width + 10, table_y - 10, "Date")
        c.drawString(table_x + col_width * 2 + 10, table_y - 10, "Amount")

        # Draw data with borders
        y = table_y - row_height
        for sale in sales_data:
            order_id = str(sale.id)
            date = sale.date.strftime("%Y-%m-%d")
            amount = f"${float(sale.amount):.2f}"

            y -= row_height
            c.line(table_x, y, table_x + table_width, y)
            c.drawString(table_x + 10, y - 10, order_id)
            c.drawString(table_x + col_width + 10, y - 10, date)
            c.drawString(table_x + col_width * 2 + 10, y - 10, amount)

        # Draw the bottom line
        c.line(
            table_x,
            table_y - table_height,
            table_x + table_width,
            table_y - table_height,
        )

        c.showPage()
        c.save()

        return response


def get_orders_by_month(request):
    orders_by_month = [0] * 12

    orders = Order.objects.all()

    for order in orders:
        month = order.order_date.month - 1
        orders_by_month[month] += 1

    return JsonResponse(orders_by_month, safe=False)


def sections_banners(request):
    sli = slider.objects.all()
    sec = Section.objects.all()
    ban = banner_area.objects.all()
    return render(request,'adminn/pages/tables/sections.html',{'sec':sec,'ban':ban,'sli':sli})

def add_slider(request):
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sections_banners')

    form = SliderForm()
    return render(request, 'adminn/pages/tables/sections.html', {'form': form})

def delete_slider(request, slide_id):
    slide = get_object_or_404(slider, pk=slide_id)  
    if request.method == 'POST':
        slide.delete()
        return redirect('sections_banners')  
    return render(request, 'adminn/pages/tables/sections.html', {'slide': slide})


def add_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sections_banners')

    form = BannerForm()
    return render(request, 'adminn/pages/tables/sections.htm', {'form': form})


def delete_banner(request,banner_id):
    banner = get_object_or_404(banner_area,pk=banner_id)
    if request.method == 'POST':
        banner.delete()
        return redirect('sections_banners')
    return render(request, 'adminn/pages/tables/sections.htm',{'banner': banner})


def add_section(request):
    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sections_banners')

    form = SectionForm()
    return render(request, 'adminn/pages/tables/sections.htm', {'form': form})



def delete_section(request,section_id):
    section = get_object_or_404(Section,pk=section_id)
    if request.method == 'POST':
        section.delete()
        return redirect('sections_banners')
    return render(request, 'adminn/pages/tables/sections.htm',{'section': section})



@never_cache
@login_required(login_url="admin_login")
def admin_users(request):
    users = CustomUser.objects.filter(is_staff=False).order_by("-id")
    per_page = 5
    paginator = Paginator(users, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "users": page_obj,
    }
    return render(request, "adminn/pages/tables/users_list.html", context)


def block_user(request, id):
    user = CustomUser.objects.get(id=id)
    user.is_active = False
    user.save()
    print("blocked")
    return redirect("users")


def unblock_user(request, id):
    user = CustomUser.objects.get(id=id)
    user.is_active = True
    user.save()
    return redirect("users")


@never_cache
@login_required(login_url="admin_login")
def product(request):
    main_cat = Main_category.objects.all()
    product = Product.objects.all().order_by("-id").filter(is_deleted=False)
    per_page = 5
    paginator = Paginator(product, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"product": page_obj, "main_cat": main_cat}
    return render(request, "adminn/pages/tables/product.html", context)


def add_product(request):
    cat = Main_category.objects.all()
    sec = Section.objects.all()

    if request.method == "POST":
        quantity = request.POST.get("total_quantity")
        availability = request.POST.get("availability")
        product_name = request.POST.get("product_name")
        featured_image = request.FILES.get("featured_image")
        price = request.POST.get("price")
        discount = request.POST.get("discount")
        tax = request.POST.get("tax")
        product_information = request.POST.get("product_information")
        model_name = request.POST.get("model_name")
        category_id = request.POST.get("categories")
        tags = request.POST.get("tags")
        description = request.POST.get("description")
        section_id = request.POST.get("section")

        try:
            category = Category.objects.get(id=category_id)
            section = Section.objects.get(id=section_id)
        except Category.DoesNotExist or Section.DoesNotExist:

            return HttpResponse("Category or Section does not exist")

        new_product = Product.objects.create(
            total_quantity=quantity,
            availability=availability,
            product_name=product_name,
            featured_image=featured_image,
            price=price,
            tax=tax,
            discount=discount,
            description=description,
            product_information=product_information,
            model_name=model_name,
            categories=category,
            tags=tags,
            section=section,
        )

        for image in request.FILES.getlist("images"):
            Product_image.objects.create(product=new_product, image_url=image)

        return redirect("product")

    return render(
        request, "adminn/pages/tables/add_product.html", {"cat": cat, "sec": sec}
    )


def edit_products(request, id):
    cat = Main_category.objects.all()
    sec = Section.objects.all()
    prod = Product.objects.get(id=id)

    context = {"prod": prod, "cat": cat, "sec": sec}

    return render(request, "adminn/pages/tables/edit_product.html", context)


def update_product(request, id):
    cat = Category.objects.all()
    sec = Section.objects.all()
    prod = Product.objects.get(id=id)
    if request.method == "POST":
        prod.total_quantity = request.POST.get("total_quantity")
        prod.availability = request.POST.get("availability")
        prod.product_name = request.POST.get("product_name")
        if "featured_image" in request.FILES:
            prod.featured_image = request.FILES.get("featured_image")
        prod.price = request.POST.get("price")
        prod.discount = request.POST.get("discount")
        prod.tax = request.POST.get("tax")
        prod.product_information = request.POST.get("product_information")
        prod.model_name = request.POST.get("model_name")
        categorie_id = request.POST.get("categories")
        prod.tags = request.POST.get("tags")
        prod.description = request.POST.get("description")
        section_id = request.POST.get("section")
        images = request.FILES.getlist("image_url")

        s = Section.objects.get(id=section_id)
        c = Category.objects.get(id=categorie_id)
        prod.categories = c
        prod.section = s
        prod.save()
        if images:
            for img in images:
                product_image = Product_image(product=prod)
                product_image.image_url = img
                product_image.save()

        return redirect("product")

    else:
        context = {"prod": prod, "cat": cat, "sec": sec}

    return render(request, "adminn/pages/tables/edit_product.html", context)


def delete_product(request, id):
    prod = Product.objects.get(id=id)
    prod.is_deleted = True
    prod.save()
    return redirect("product")


@never_cache
@login_required(login_url="admin_login")
def category(request):
    maincategory = Main_category.objects.all().order_by("id").filter(is_deleted=False)

    context = {
        "maincategory": maincategory,
    }
    return render(request, "adminn/pages/tables/category.html", context)


def add_main_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        cat = Main_category(name=name)
        cat.save()
        return redirect("category")

    return render(request, "adminn/pages/tables/add_maincategory.html")


def edit_main_category(request, id):
    cat = Main_category.objects.get(id=id)
    print(cat)
    context = {
        "cat": cat,
    }
    return render(request, "adminn/pages/tables/edit_maincategory.html", {"cat": cat})


def update_maincategory(request, id):
    cat = Main_category.objects.get(id=id)
    print(cat)
    if request.method == "POST":
        print("post")
        new_name = request.POST.get("category_name")
        cat.name = new_name
        cat.save()
        print(cat.name)
        return redirect("category")
    else:
        return render(
            request, "adminn/pages/tables/edit_maincategory.html", {"cat": cat}
        )


def delete_maincategory(request, id):
    cat = Main_category.objects.get(id=id)
    cat.is_deleted = True
    cat.save()
    return redirect("category")


@never_cache
@login_required(login_url="admin_login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def subcategory(request):
    category = Main_category.objects.all().order_by("id").filter(is_deleted=False)
    subcategory = Category.objects.all().order_by("id").filter(is_deleted=False)
    context = {"category": category, "subcategory": subcategory}

    return render(request, "adminn/pages/tables/sub_category.html", context)


def add_subcategory(request):
    maincategory = Main_category.objects.all()
    context = {"maincategory": maincategory}
    if request.method == "POST":
        cat = request.POST.get("categories")
        name = request.POST.get("name")
        main = Main_category.objects.get(id=cat)
        add = Category.objects.create(main_category=main, name=name)
        return redirect("subcategory")

    return render(request, "adminn/pages/tables/add_subcategory.html", context)


def edit_subcategory(request, id):
    main = Main_category.objects.all()
    cat = Category.objects.get(id=id)
    return render(
        request, "adminn/pages/tables/edit_subcategory.html", {"cat": cat, "main": main}
    )


def update_subcategory(request, id):
    main = Main_category.objects.all()
    sub = Category.objects.get(id=id)
    if request.method == "POST":
        new_name = request.POST.get("subcategory_name")
        new_main_id = request.POST.get("main_category")
        sub.name = new_name
        sub.main_category_id = new_main_id
        sub.save()
        return redirect("subcategory")

    return render(request, "adminn/pages/tables/edit_subcategory.html")


def delete_subcategory(request, id):
    try:
        sub = Category.objects.get(id=id)
        sub.is_deleted = True
        sub.save()
        print(sub.is_deleted)
    except Category.DoesNotExist:
        return HttpResponse("Not found")

    return redirect("subcategory")


@never_cache
@login_required(login_url="admin_login")
def orders(request):
    orders = Order.objects.all().order_by("-id")
    for i in orders:
        print(i.product)
    return render(request, "adminn/pages/tables/orders.html", {"orders": orders})


def update_order(request, id):
    order = Order.objects.get(id=id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        print(new_status)
        order.status = new_status
        order.save()
        return redirect("orders")
    return render(request, "adminn/pages/tables/update_order.html", {"order": order})


@never_cache
@login_required(login_url="admin_login")
def coupon(request):
    coupons = Coupon.objects.all().order_by("-id")
    return render(request, "adminn/pages/tables/coupon.html", {"coupons": coupons})


def add_coupon(request):
    if request.method == "POST":
        code = request.POST.get("code")
        discount = request.POST.get("discount")
        start_date = request.POST.get("start_date")
        expiration_date = request.POST.get("expiration_date")
        new_coupon = Coupon.objects.create(
            code=code,
            discount=discount,
            start_date=start_date,
            expiration_date=expiration_date,
        )
        new_coupon.save()
        return redirect("coupon")


def activate_coupon(request, id):
    coupon = Coupon.objects.get(id=id)
    coupon.status = True
    coupon.save()
    return redirect("coupon")


def deactivate_coupon(request, id):
    coupon = Coupon.objects.get(id=id)
    coupon.status = False
    coupon.save()
    return redirect("coupon")


def delete_coupon(request, id):
    coupon = Coupon.objects.get(id=id)
    coupon.delete()
    return redirect("coupon")


@never_cache
@login_required(login_url="admin_login")
def admin_reviews(request):
    reviews = ProductReview.objects.annotate(star_count=F("star_rating")).order_by(
        "-star_count"
    )
    return render(
        request,
        "adminn/pages/tables/admin_reviews.html",
        {"reviews": reviews, "product": product},
    )


@never_cache
@login_required(login_url="admin_login")
def offer(request):
    all_categories = Category.objects.filter(is_deleted=False)
    all_offers = Offer.objects.all()
    context = {
        "all_categories": all_categories,
        "all_offers": all_offers,
    }
    return render(request, "adminn/pages/tables/offer.html", context)


def add_offer(request):
    if request.method == "POST":
        title = request.POST["title"]
        discount = request.POST["discount"]
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        Offer.objects.create(
            title=title, discount=discount, start_date=start_date, end_date=end_date
        )
        return redirect("offer")

    return render(request, "adminn/pages/tables/offer.html")


def add_offer_to_category(request):
    error_message = ""
    if request.method == "POST":
        category_id = request.POST.get("category")
        print("category_id:", category_id)
        category = get_object_or_404(Category, id=category_id)
        offer_id = request.POST.get("offer")
        offer = get_object_or_404(Offer, id=offer_id)

        if not category.offers.filter(id=offer_id).exists():
            category.offers.add(offer)
            return redirect("offer")
        else:
            error_message = "Offer is already associated with this category."

    all_categories = Category.objects.all()
    all_offers = Offer.objects.all()

    return render(
        request,
        "adminn/pages/tables/offer.html",
        {
            "selected_category": category,
            "all_categories": all_categories,
            "all_offers": all_offers,
            "error_message": error_message,
        },
    )



class NotificationListView(ListView):
    model = Notification
    template_name = "adminn/pages/tables/notification.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


def admin_search(request):
    search_form = GlobalSearchForm(request.GET)
    search_query = request.GET.get("search_query", "")

    users = CustomUser.objects.filter(
        Q(email__icontains=search_query)
        | Q(first_name__icontains=search_query)
        | Q(last_name__icontains=search_query)
    )
    categories = Main_category.objects.filter(name__icontains=search_query)
    subcategories = Category.objects.filter(name__icontains=search_query)
    orders = Order.objects.filter(
        Q(id__icontains=search_query) | Q(status__icontains=search_query)
    )
    reviews = ProductReview.objects.filter(review_text__icontains=search_query)
    coupons = Coupon.objects.filter(
        Q(code__icontains=search_query) | Q(discount__icontains=search_query)
    )
    offers = Offer.objects.filter(
        Q(title__icontains=search_query) | Q(discount__icontains=search_query)
    )
    notifications = Notification.objects.filter(message__icontains=search_query)

    context = {
        "search_form": search_form,
        "search_query": search_query,
        "users": users,
        "categories": categories,
        "subcategories": subcategories,
        "orders": orders,
        "reviews": reviews,
        "coupons": coupons,
        "offers": offers,
        "notifications": notifications,
    }

    return render(request, "adminn/pages/tables/global_search.html", context)
