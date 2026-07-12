from django.urls import path
from . import views

urlpatterns = [
    path('', views.driver_list, name='driver_list'),
    path('add/', views.driver_add, name='driver_add'),
    path('<int:pk>/', views.driver_detail, name='driver_detail'),
    path('<int:pk>/edit/', views.driver_edit, name='driver_edit'),
    path('<int:pk>/delete/', views.driver_delete, name='driver_delete'),
    path('<int:pk>/send-reminder/', views.send_license_reminder, name='send_license_reminder'),
    path('send-all-reminders/', views.send_all_reminders, name='send_all_reminders'),
]
