from django.urls import path
from crypto import views

urlpatterns = [
    path("transactions/", views.get_wallet_transactions),
    path("register/", views.register_user),
    path("login/", views.login_user),
    path("verify/", views.verify_email),
    path("resend_otp/", views.resend_otp),
    path("profiles/", views.get_profiles),
    path("logout/", views.logout_user),
    path("add_wallet_address/", views.add_wallet_address),
    path("add_coin/", views.add_coin),
    path("get_user_coins/", views.get_user_coins),
    path("user_address_by_id/", views.fetch_address_identifier),
]
