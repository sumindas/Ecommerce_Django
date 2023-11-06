from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from adminn import views
from django.contrib import admin


urlpatterns = [
    path('',views.admin_login,name='admin_login'),
    path('admin_base/',views.admin_base,name = 'admin_base'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('index',views.admin_index,name='index'),
    path('users/',views.admin_users,name='users'),
    path('category/',views.category,name='category'),
    path('product',views.product,name='product'),
    
    #user
    
    path('block_user/<int:id>',views.block_user,name='block_user'),
    path('unblock_user/<int:id>',views.unblock_user,name='unblock_user'),
    
    #category
    
    path('add-maincategory',views.add_main_category,name='add-maincategory'),
    path('edit_maincategory/<int:id>',views.edit_main_category,name='edit_maincategory'),
    path('update_maincategory/<int:id>',views.update_maincategory,name='update_maincategory'),
    path('delete_maincategory/<int:id>',views.delete_maincategory,name='delete_maincategory'),
    
    
    #subcategory
    
    path('subcategory',views.subcategory,name='subcategory'),
    path('edit_subcategory/<int:id>',views.edit_subcategory,name='edit_subcategory'),
    path('update_subcategory/<int:id>',views.update_subcategory,name='update_subcategory'),
    path('add_subcategory',views.add_subcategory,name='add_subcategory'),
    path('delete_subcategory/<int:id>',views.delete_subcategory,name='delete_subcategory'),
    
    
    #product
    
    path('add_product',views.add_product,name='add_product'),
    path('view_product',views.view_product,name = 'view_product'),
    path('edit_product/<int:id>',views.edit_products,name='edit_product'),
    path('update_product/<int:id>',views.update_product,name='update_product'),
    path('delete_product/<int:id>',views.delete_product,name='delete_product'),
    path('coupon',views.coupon,name='coupon'),
    path('add_coupon',views.add_coupon,name='add_coupon'),
    path('activate_coupon/<int:id>',views.activate_coupon,name='activate_coupon'),
    path('deactivate_coupon/<int:id>',views.deactivate_coupon,name='deactivate_coupon'),
    path('delete_coupon/<int:id>',views.delete_coupon,name='delete_coupon'),
    
    #orders
    
    path('orders',views.orders,name='orders'),
    path('update_order/<int:id>',views.update_order,name='update_order'),
    path('admin_reviews',views.admin_reviews,name='admin_reviews'),
    path('reply_to_review/<int:review_id>/', views.reply_to_review, name='reply_to_review'),
    path('offer',views.offer,name='offer'),
    path('add_offer',views.add_offer,name='add_offer'),
    path('add_offer_to_category', views.add_offer_to_category, name='add_offer_to_category'),
    
    #index
    path('generate_pdf_sales_report',views.generate_pdf_sales_report,name='generate_pdf_sales_report'),
    path('get_orders_by_month',views.get_orders_by_month,name='get_orders_by_month'),
    path('notifications',views.NotificationListView.as_view(),name='notifications'),
    
    
    #Admin_Search
    path('admin_search',views.admin_search,name='admin_search'),
    
    
]
