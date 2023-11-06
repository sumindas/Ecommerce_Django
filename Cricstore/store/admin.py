from django.contrib import admin
from store.models import *

# Register your models here.

admin.site.register(slider)
admin.site.register(banner_area)
admin.site.register(Main_category)
admin.site.register(Category)
admin.site.register(Sub_category)

class Product_images(admin.TabularInline):
    model = Product_image
    
class Additional_informations(admin.TabularInline):
    model = Additional_information
    
class Product_Admin(admin.ModelAdmin):
    inlines = (Product_images,Additional_informations)
    list_display = ('product_name','price','categories','section')
    list_editable = ('categories','section')


admin.site.register(Section)
admin.site.register(Product,Product_Admin)
admin.site.register(Additional_information)
admin.site.register(Product_image)

