from django.urls import path
from . import views
from .profile_views import profile_view

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('save-location/', views.save_location, name='save_location'),
    path('profile/', profile_view, name='profile'),
]