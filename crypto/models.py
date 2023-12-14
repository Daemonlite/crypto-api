from django.db import models
from crypto.caches import Cache
import uuid
from django.utils import timezone


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
    first_login = models.DateTimeField(null=True)
    last_login = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.username)


class Wallet(models.Model):
    address = models.CharField(max_length=120, blank=True, null=True)
    holder = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    identifier = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return str(self.address)


class Coin(models.Model):
    holder = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=120, blank=True, null=True)
    wallet_addresses = models.ManyToManyField(Wallet, blank=True)
    symbol = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return str(self.name)
