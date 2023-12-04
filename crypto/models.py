from django.db import models
from crypto.caches import Cache
from crypto.utils import CoinManager
from decimal import Decimal
import uuid

# Create your models here.
manager = CoinManager()


# TODO:update coin model to store mutliple addresses for a single coin
class Profile(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=120, blank=True, null=True)
    username = models.CharField(max_length=120, blank=True, null=True)
    email = models.CharField(max_length=120, blank=True, null=True)
    phone = models.CharField(max_length=120, blank=True, null=True)
    address = models.CharField(max_length=120, blank=True, null=True)
    password = models.CharField(max_length=120, blank=True, null=True)
    isbanned = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)


class Coin(models.Model):
    holder = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, blank=True, null=True
    )
    name = models.CharField(max_length=120, blank=True, null=True)
    wallet_address = models.CharField(max_length=3000, blank=True, null=True)
    symbol = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache = Cache(Coin, "cache_coins")
        cache.save_values()
        return super().save(*args, **kwargs)

    def fetch_coins(self):
        return Cache(Coin, "cache_coins").fetch_values()
