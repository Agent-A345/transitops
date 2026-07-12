from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('vehicles.urls')),
    path('drivers/', include('drivers.urls')),
    path('trips/', include('trips.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('fuel/', include('fuel.urls')),
]