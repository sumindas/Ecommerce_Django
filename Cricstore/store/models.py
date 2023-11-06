from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from user.models import *
from django.db.models.signals import pre_save
from datetime import datetime
from django.utils import timezone
# Create your models here.


class slider(models.Model):
    
    DISCOUNT_DEAL = (
        ('HOT DEALS','HOT DEALS'),
        ('New Arrivals','New Arrivals'),
    )
    image = models.ImageField(upload_to='slider_img')
    discount_deal = models.CharField(choices=DISCOUNT_DEAL,max_length=100)
    sale = models.IntegerField()
    brand_name = models.CharField(max_length=200)
    discount = models.IntegerField()
    link = models.CharField(max_length=200)
    
    
    
    def __str__(self):
        return self.brand_name
    
    


class banner_area(models.Model):
    image = models.ImageField(upload_to='banner_img')
    discount_deal = models.CharField(max_length=100)
    quotes = models.CharField(max_length=100)
    discount = models.IntegerField()
    link = models.CharField(max_length=200,null=True)
    
    
    def __str__(self):
        return self.quotes

class Offer(models.Model):
    title = models.CharField(max_length=100)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    

    def __str__(self):
        return self.title


class Main_category(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.name


class Category(models.Model):
    main_category =models.ForeignKey(Main_category,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)
    offers = models.ManyToManyField(Offer, related_name='categories', blank=True,through='store.OfferCategory')
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        
        return {
            'id': self.id,
            'main_category': self.main_category.id,
            'name': self.name,
            'is_deleted': self.is_deleted,
            
        }


class OfferCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('category', 'offer')

class Sub_category(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)     
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.category.main_category.name + " -- " + self.category.name + " -- " + self.name



class Section(models.Model):
    name = models.CharField(max_length=100)
    
    
    def __str__(self):
        return self.name


class Product(models.Model):
    total_quantity = models.IntegerField()
    availability = models.IntegerField()
    featured_image =  models.ImageField(upload_to='media/product_imgs')
    product_name = models.CharField(max_length=100)
    price = models.IntegerField()
    discount = models.IntegerField(blank=True)
    tax = models.IntegerField(null = True)
    packing_cost = models.IntegerField(null = True)
    product_information = RichTextField() 
    model_name = models.CharField(max_length=100)
    categories = models.ForeignKey(Category,on_delete=models.CASCADE)
    tags = models.CharField(max_length=100)
    description = RichTextField()
    section = models.ForeignKey(Section,on_delete=models.DO_NOTHING)
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    
    def __str__(self):
        return self.product_name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("product_detail", kwargs={"slug": self.slug})
    
    
        
def create_slug(instance,new_slug = None):
    slug = slugify(instance.product_name)
    if new_slug is not None:
        slug = new_slug
    qs = Product.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug,qs.first().id)
        return create_slug(instance,new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver,Product) 
    
    
    
class Product_image(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to ='media/product_imgs')
    

class Additional_information(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification = models.CharField(max_length=100)
    detail = models.CharField(max_length=100)




