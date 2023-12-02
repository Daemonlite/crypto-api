from django.contrib import admin
from crypto.models import Countries, Rates, Coin
# Register your models here.

@admin.register(Countries)
class CountriesAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in Countries._meta.fields)
    search_fields = ["name", "short_code"]

@admin.register(Rates)
class RatesAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in Rates._meta.fields)
    search_fields = ["country__name", "coin__name"]

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in Coin._meta.fields)
    search_fields = ["name", "short_code"]