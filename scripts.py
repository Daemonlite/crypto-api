import os
import django
import requests
from crypto.caches import Cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digest.settings")
django.setup()


from crypto.utils import CoinManager
from django.core.cache import cache

mana = CoinManager()
# fee = mana.coin_market_rates()


# print(fee.get('ethereum'))

eth = "0x32bd825f30BA59234c9c3620237f0b14249B109F"
btc = "bc1q0jfpa8xkg2v9yslkxs99yj4scarkqn5sge2nnk"
ltc = "ltc1qv7wsvsmx6tqxjz9l750n0pj524na4lmqrjhyz9"
xrp = "rBURNERRhpAM8ygERz7GsXrHRjJrngBLi2"


mn = 1727574 / 10**8
print(mn)
