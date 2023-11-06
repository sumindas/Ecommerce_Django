from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from user import views
from django.conf.urls.static import static

urlpatterns = [
    
    #Account
    
    path('',views.myaccount,name = 'myaccount'),
    path('register/',views.register,name='register'),
    path('verified_login',views.verified_login,name='verified_login'),
    path('verify_otp/', views.verify_signup, name='verify_signup'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('logout',views.logout,name='logout'),
    
    #Profile
    
    path('profile/',views.profile,name='profile'),
    path('profile_update/',views.profile_update,name='profile_update'),
    path('add_address/',views.add_address,name="add_address"),
    path('address/',views.address,name="address"),
    path('edit_address/<int:id>',views.edit_address,name="edit_address"),
    path('update_address/<int:id>',views.update_address,name='update_address'),
    path('delete_address/<int:id>',views.delete_address,name='delete_address'),
    
    #Order
    
    path('place_order',views.place_order,name='place_order'),
    path('order_success',views.order_success,name='order_success'),
    path('return_order/<int:order_id>',views.return_order,name='return_order'),
    path('order_list',views.order_list,name='orders_list'),
    path('order_details/<int:order_id>',views.order_details,name='order_details'),
    path('order_cancel/<int:id>',views.order_cancel,name='order_cancel'),
    path('generate_invoice_pdf/<int:order_id>',views.generate_invoice_pdf,name='generate_invoice_pdf'),
    
    #Wishlist
    
    path('wishlist',views.wishlist,name='wishlist'),
    path('add_to_wish/<int:id>',views.add_to_wish,name='add_to_wish'),
    path('remove_from_wishlist/<int:id>',views.remove_from_wishlist,name='remove_from_wishlist'),
    
    #Payment
    
    path('razorpay_payment',views.razorpay_payment,name='razorpay_payment'),
    path('wallet',views.wallet,name='wallet'),
    
    

    
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


