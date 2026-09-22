from django.urls import path
from . import views

urlpatterns = [
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('master/', views.master_dashboard, name='master_dashboard'),
    path('master/history/', views.master_orders_history, name='master_orders_history'),
    path('order/<int:order_id>/accept/', views.accept_order, name='accept_order'),
    path('order/<int:order_id>/start/', views.start_order, name='start_order'),
    path('order/<int:order_id>/complete/', views.complete_order, name='complete_order'),
]
