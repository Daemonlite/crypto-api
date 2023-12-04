from django.contrib import admin
from crypto.models import Coin, Profile, WalletAddress

# Register your models here.


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in Coin._meta.fields)
    search_fields = ["name", "holder__username"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in Profile._meta.fields)
    search_fields = ["username", "first_name", "last_name"]


@admin.register(WalletAddress)
class WalletAddressAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in WalletAddress._meta.fields)
    search_fields = ["address"]
