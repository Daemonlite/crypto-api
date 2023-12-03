from django.urls import path
from . import views

urlpatterns = [
    path("eth_btc/", views.get_latest_transactions),
    path("ltc_usdt/", views.get_lc_transactions),
]
