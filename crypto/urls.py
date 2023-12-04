from django.urls import path
from crypto import views

urlpatterns = [
    path("transactions/", views.get_wallet_transactions),
    path("register/", views.register_user),
    path("verify/", views.verify_email),
    path("resend_otp/", views.resend_otp),
    path("profiles/", views.get_profiles),
    path("logout/", views.logout_user),
]
