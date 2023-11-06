from django.contrib import admin
from user.models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Address)