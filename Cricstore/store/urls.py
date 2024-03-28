from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path('admin/',admin.site.urls),
    path('base',views.base,name='base'),
    
    path('',views.home,name='home'),
    path('product/<slug:slug>',views.product_detail,name='product_detail'),
    path('mayaccount',views.myaccount,name='myaccount'),
    path('shop',views.shop,name='shop'),
    path('search_suggestions',views.search_suggestions,name='search_suggestions'),
    path('category/<str:main_category>/',views.category_products, name='category_products'),
    path('cart',views.cart_detail,name='cart'),
    path('cart/add/<int:id>', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:product_id>/',views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:product_id>/',views.item_decrement, name='item_decrement'),
    path('cart/cart_clear/', views.cart_clear, name='cart_clear'),
    path('update_cart_item/<int:product_id>/<str:action>/', views.update_cart, name='update_cart_item'),
    path('get_cart_data/',views.get_cart_data,name='get_cart_data'),
    path('checkout/',views.checkout,name='checkout'),
   
    
    
    
    # path('product_filter',views.product_filter,name='product_filter'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
