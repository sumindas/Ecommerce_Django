
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from store.views import custom_404


handler404 = custom_404
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('store.urls')),
    path('user/',include('user.urls')),
    path('adminn/',include('adminn.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
