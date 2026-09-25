from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('orders/<int:order_id>/review/', views.submit_review, name='submit_review'),
]

# ==========================================================
# Asosiy loyiha urls.py (masalan config/urls.py yoki
# loyiha_nomi/urls.py) fayliga qo'shing:
#
#   path('', include('reviews.urls')),
# ==========================================================