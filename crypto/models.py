from django.db import models
from crypto.caches import Cache
from decimal import Decimal
# Create your models here.

class Coin(models.Model):
    network = models.CharField(max_length=10, blank=True, null=True)
    placeholder = models.CharField(max_length=100, blank=True, null=True)
    value = models.CharField(max_length=20, blank=True, null=True)
    token = models.CharField(max_length=10, blank=True, null=True)
    image = models.CharField(max_length=200, blank=True, null=True)
    coin = models.CharField(max_length=10, blank=True, null=True)
    label = models.CharField(max_length=20, blank=True, null=True)
    stable = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    current_price = models.CharField(max_length=10, blank=True, null=True)
    cache_key = models.CharField(
        max_length=20, blank=True, null=True
    )  # used to identify the key to allow for caching in task update_coin_data
    price_change_percentage_24h = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return str(self.coin)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache = Cache(Coin, "cache_coins")
        cache.save_values()
        return super().save(*args, **kwargs)

    def fetch_coins(self):
        return Cache(Coin, "cache_coins").fetch_values()
    

class Countries(models.Model):
    name = models.CharField(max_length=120, blank=True, null=True)
    # eg 233 for ghana
    short_code = models.CharField(max_length=5, blank=True, null=True)
    currency_code = models.CharField(max_length=5, blank=True, null=True)
    currency = models.CharField(max_length=120, blank=True, null=True)
    allow_use = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Cache(Countries, "cache_countries").save_values()
        return super().save(*args, **kwargs)

    def fetch_countries(self, country=None, country_id=None):
        cached_data = Cache(Countries, "cache_countries").fetch_values()
        if country:
            country = [
                country_ for country_ in cached_data if country_["name"] == country
            ]
            if len(country) > 0:
                return country[0]
            return None
        if country_id:
            country = [
                country_ for country_ in cached_data if country_["id"] == country_id
            ]
            if len(country) > 0:
                return country[0]
            return None
        return Cache(Countries, "cache_countries").fetch_values()
    

class Rates(models.Model):
    """meant for setting country specific rates for each coin"""

    buy = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal(0))
    sell = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal(0))
    send = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal(0))
    fees = models.TextField(blank=True, null=True)
    coin = models.ForeignKey("Coin", on_delete=models.DO_NOTHING, blank=True, null=True)
    country = models.ForeignKey(
        "Countries", on_delete=models.DO_NOTHING, blank=True, null=True
    )
    category = models.CharField(max_length=120, blank=True, null=True)
    percentage = models.BooleanField(default=False)
    allow_buy = models.BooleanField(default=True)
    allow_sell = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.country.name != "Ghana":
            Rates.objects.exclude(country__name="Ghana").update(
                buy=self.buy, sell=self.sell
            )
        super().save(*args, **kwargs)
        Cache(Rates, "cache_rates").save_values()
        return super().save(*args, **kwargs)

    def fetch_rates(self, template=None):
        if template:
            coin_id = Cache(Coin, "cache_coins").fetch_values()
            for coin in coin_id:
                if coin["value"] == template["coin"]:
                    coin_id = coin["id"]
                    break
            cached_rates = Cache(Rates, "cache_rates").fetch_values()
            cached_country = Countries().fetch_countries(country=template["name"])
            if cached_country:
                country = None
                country_id = cached_country["id"]
                for rate in cached_rates:
                    if rate["country_id"] == country_id and rate["coin_id"] == coin_id:
                        country = rate
                        break
                return country
            return None
        return Cache(Rates, "cache_rates").fetch_values()

    def fetch_rates_by_country(self, country):
        cached_rates = Cache(Rates, "cache_rates").fetch_values()
        cached_coins = Cache(Coin, "cache_coins").fetch_values()
        cached_country = Countries().fetch_countries(country=country)
        returns = []
        if cached_country:
            country_id = cached_country["id"]
            for rate in cached_rates:
                if rate["country_id"] == country_id:
                    coin = [
                        coin["value"]
                        for coin in cached_coins
                        if rate["coin_id"] == coin["id"] and coin["trade_direct"]
                    ][0]
                    rates = {"buy": rate["buy"], "sell": rate["sell"], "coin": coin}
                    returns.append(rates)
        if len(returns) > 0:
            return returns
        return None