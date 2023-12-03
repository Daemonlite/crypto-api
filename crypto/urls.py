from django.urls import path
from crypto import views

urlpatterns = [
    path("transactions/", views.get_wallet_transactions),
]
