
from django.urls import path
from . import views

urlpatterns = [
    path(
        'category/<slug:slug>/',
        views.category_detail,
        name='category_detail'
    ),

    path(
        'category/<slug:slug>/order/',
        views.create_order,
        name='create_order'
    ),

    path(
        'category/<slug:slug>/order/<int:master_id>/',
        views.create_order_for_master,
        name='create_order_for_master'
    ),

    path(
        'connect-telegram/',
        views.connect_telegram,
        name='connect_telegram'
    ),
]

