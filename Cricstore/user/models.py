from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from store.models import *
from datetime import date,datetime

from store.models import Product

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    full_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    ph_no=models.CharField(max_length=15,blank=True)
    wallet_bal = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    
    
    objects = CustomUserManager()
    
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
    )


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def __iter__(self):
        yield self.id 
        
        
class Address(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=False, blank=True)
    last_name = models.CharField(max_length=50, null=False,blank=True)
    email = models.EmailField()
    number = models.BigIntegerField(blank=True)
    address = models.CharField(max_length=250)
    country = models.CharField(max_length=15)
    state = models.CharField(max_length=15)
    city = models.CharField(max_length=15)
    pin_code = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.address}, {self.city}, {self.state} - {self.user}"


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='cart', null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)
   
    
    
    
    def __str__(self):
        return f"{self.user.full_name}'s Cart: {self.product.product_name} - Quantity: {self.quantity}"
    

    
    
class Order(models.Model):

    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing','processing'),
        ('shipped','shipped'),
        ('delivered','delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded','refunded'),
        ('on_hold','on_hold')

    )

    user           =   models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    address        =   models.ForeignKey(Address, on_delete=models.SET_NULL,null=True,blank=True)
    product        =   models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    amount         =   models.CharField(max_length=100)  
    payment_type   =   models.CharField(max_length=100)  
    status         =   models.CharField(max_length=100, choices=ORDER_STATUS, default='pending' )  
    quantity       =   models.IntegerField(default=0, null=True, blank=True)
    image          =   models.ImageField(upload_to='products', null=True, blank=True)
    date           =   models.DateField(default=date.today) 
    
        
    def __str__(self):
        return f"Order #{self.pk} - {self.product}"
    
class OrderItem(models.Model):
    order          =   models.ForeignKey(Order,on_delete=models.CASCADE)
    product        =   models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity       =   models.IntegerField(default=1)
    image          =   models.ImageField(upload_to='products_order', null=True, blank=True)

    def __str__(self):
        return str(self.id)

class OrderAddress(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    address = models.ForeignKey(Address,on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return self.order

class ReturnOrder(models.Model):
    original_order = models.ForeignKey(Order, on_delete=models.CASCADE)
    return_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Return Order for Order #{self.original_order.id}'
    
class ReturnOrderItem(models.Model):
    return_order = models.ForeignKey(ReturnOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'Return of {self.quantity} {self.product} for Return Order #{self.return_order.id}'

class WishList(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products',null = True,blank=True)
    
    def __str__(self):
        return f"{self.user.full_name}'s Wishlist Item:{self.product.product_name}"


class ProductReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review_text = models.TextField()
    star_rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
       
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.IntegerField()
    start_date = models.DateField(default='2023-10-12')
    expiration_date = models.DateField()
    status = models.BooleanField(default=True)
    users = models.ManyToManyField(CustomUser, blank=True)

    def __str__(self):
        return self.code

class UserWallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_credit = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def _str_(self):
       return f"{self.balance} {'Credit' if self.is_credit else 'Debit'}"

    def _iter_(self):
        yield self.pk
        yield self.balance
        yield self.is_credit 

class WalletTransaction(models.Model):
    wallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.timestamp} - {self.description}: Rs {self.amount}"
    

class UserCouponUsage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code} ({'Used' if self.used else 'Not Used'})"
    

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    event_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)