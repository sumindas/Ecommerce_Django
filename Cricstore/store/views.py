from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from store.models import *
from user.models import *
from user.models import CartItem
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from django.http import JsonResponse
from django.db.models import Q, F
from .forms import ProductReviewForm
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def base(request):
    main_category = Main_category.objects.all().order_by("-id")
    context = {
        "main_category": main_category,
    }
    return render(request, "base.html", context)


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    sliders = slider.objects.all().order_by("-id")[:3]
    banners = banner_area.objects.all().order_by("-id")[:3]
    sections = Section.objects.all()
    main_category = Main_category.objects.all().order_by("-id")
    product = Product.objects.all()
    product_image = Product_image.objects.all()
    context = {
        "sliders": sliders,
        "banners": banners,
        "main_category": main_category,
        "products": product,
        "sections": sections,
        "product_image": product_image,
    }
    return render(request, "Main/home.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            user = request.user
            if user_has_purchased_product(user, product):
                name = form.cleaned_data["user_name"]
                email = form.cleaned_data["user_email"]
                review_text = form.cleaned_data["review_text"]
                star_rating = form.cleaned_data["star_rating"]

                ProductReview.objects.create(
                    user=user,
                    user_name=name,
                    user_email=email,
                    review_text=review_text,
                    star_rating=star_rating,
                    product=product,
                )

                return redirect("product_detail", slug=slug)
            else:
                return HttpResponse("Item Need To be Purchased")
    else:
        form = ProductReviewForm()

    reviews = ProductReview.objects.filter(product=product)

    context = {
        "product": product,
        "reviews": reviews,
        "form": form,
    }

    return render(request, "product/product-detail.html", context)


def user_has_purchased_product(user, product):
    return Order.objects.filter(user=user, product=product).exists()


def myaccount(request):
    return HttpResponse("myaccount")


def shop(request):
    main_category = Category.objects.all().order_by("-id")
    product = Product.objects.all()
    selected_category = request.GET.getlist("category")
    search_query = request.GET.get("q")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    suggestions = None

    if search_query:
        suggestions = (
            Product.objects.annotate(
                search=SearchVector("product_name", "categories__name"),
            )
            .filter(search=SearchQuery(search_query))
            .annotate(rank=SearchRank(F("search"), SearchQuery(search_query)))
            .order_by("-rank")
        )

        product = product.filter(
            Q(product_name__icontains=search_query)
            | Q(categories__name__icontains=search_query)
        )

    if selected_category:
        product = product.filter(categories__in=selected_category, is_deleted=False)

    if min_price and max_price:
        product = product.filter(price__gte=min_price, price__lte=max_price)

    page = request.GET.get("page", 1)
    paginator = Paginator(product, 10)
    try:
        product = paginator.page(page)
    except PageNotAnInteger:
        product = paginator.page(1)
    except EmptyPage:
        product = paginator.page(paginator.num_pages)

    context = {
        "main_category": main_category,
        "product": product,
        "selected_category": selected_category,
        "suggestions": suggestions,
    }
    return render(request, "Main/shop.html", context)


from django.http import JsonResponse


def search_suggestions(request):
    query = request.GET.get("q")
    suggestions = Product.objects.filter(Q(product_name__icontains=query)).values(
        "product_name"
    )[:10]

    return JsonResponse(list(suggestions), safe=False)


def category_products(request, main_category):
    main_category = Main_category.objects.filter(name=main_category)
    if main_category.exists():
        product = Product.objects.filter(
            categories__main_category__in=main_category, is_deleted=False
        )
        return render(
            request,
            "Main/category.html",
            {
                "product": product,
                "main_categories": main_category,
            },
        )
    else:
        return render(
            request,
            "Main/category.html",
            {
                "product": [],
                "main_category": main_category,
            },
        )


def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart")


def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    CartItem.objects.filter(product=product).delete()
    cart.remove(product)
    return redirect("cart")


def item_increment(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    print(product)
    cart.add(product=product)
    return redirect("cart")


def item_decrement(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.decrement(product=product)
    return redirect("cart")


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    CartItem.objects.filter(user=request.user).delete()
    return redirect("cart")


def get_category_offers(product):
    category = product.categories
    category_offers = category.offers.all()
    print(f"Category offers for {product.product_name}: {category_offers}")
    return category_offers


def cart_detail(request):
    cart = request.session.get("cart")
    today = timezone.now().date()
    tax = sum(i["tax"] for i in cart.values() if i)

    cart_product_ids = cart.keys()
    product_category_offers = {}
    for product_id in cart_product_ids:
        product = Product.objects.get(id=product_id)
        if product.availability <= 0:
            return HttpResponse("Out of stock")
        category_offers = get_category_offers(product)
        if category_offers:
            product_category_offers[product_id] = category_offers
    product_ids = product_category_offers.keys()
    offer_keys = list(product_ids)
    for i in offer_keys:
        print(i)
    context = {
        "tax": tax,
        "product_category_offers": product_category_offers,
        "offer_keys": offer_keys,
    }
    return render(request, "Main/cart.html", context)


def update_cart(request, product_id, action):
    print(product_id, action)
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)

    if action == "increment":
        cart.add(product=product, quantity=1)
    elif action == "decrement":
        cart.decrement(product=product)
    new_quantity = cart.get_quantity(product)
    new_cart_total = cart.get_total_price()
    discounted_price = product.price - (product.price * (product.discount / 100))
    new_subtotal = discounted_price * new_quantity
    new_order_total = new_cart_total
    cart.save()

    return JsonResponse(
        {
            "new_quantity": new_quantity,
            "new_cart_total": new_cart_total,
            "new_subtotal": new_subtotal,
            "new_order_total": new_order_total,
        }
    )


def get_cart_data(request):
    cart = Cart(request)
    cart_total = cart.get_total_price()
    return JsonResponse({"cart_total": cart_total})

def custom_404(request, exception):
    return render(request, 'Error/404_Not_Found.html', {}, status=404)

@login_required(login_url="verified_login")
def checkout(request):
    cart = request.session.get("cart")
    user = request.user
    today = timezone.now().date()
    used_coupons = UserCouponUsage.objects.filter(user=user, used=True).values_list(
        "coupon", flat=True
    )
    coupons = Coupon.objects.exclude(id__in=used_coupons)
    cart_product_ids = cart.keys()
    product_category_offers = {}
    for product_id in cart_product_ids:
        product = Product.objects.get(id=product_id)
        category_offers = get_category_offers(product)
        if category_offers:
            product_category_offers[product_id] = category_offers

    address_list = Address.objects.filter(user=request.user)
    context = {
        "cart": cart,
        "address_list": address_list,
        "coupons": coupons,
        "product_category_offers": product_category_offers,
    }
    return render(request, "Main/checkout.html", context)
