from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls', namespace='users')),
    path('api/products/', include('apps.products.urls', namespace='products')),
    path('api/cart/', include('apps.cart.urls', namespace='cart')),
    
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
