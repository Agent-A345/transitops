from django.urls import path
from . import views

urlpatterns = [
    path('', views.fuel_list, name='fuel_list'),
    path('add/', views.fuel_add, name='fuel_add'),
    path('<int:pk>/delete/', views.fuel_delete, name='fuel_delete'),
    path('expense/add/', views.expense_add, name='expense_add'),
    path('expense/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
]
