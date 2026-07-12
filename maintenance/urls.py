from django.urls import path
from . import views

urlpatterns = [
    path('', views.maintenance_list, name='maintenance_list'),
    path('add/', views.maintenance_add, name='maintenance_add'),
    path('<int:pk>/', views.maintenance_detail, name='maintenance_detail'),
    path('<int:pk>/approve/', views.maintenance_approve, name='maintenance_approve'),
    path('<int:pk>/reject/', views.maintenance_reject, name='maintenance_reject'),
    path('<int:pk>/resolve/', views.maintenance_resolve, name='maintenance_resolve'),
]
