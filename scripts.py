import os
import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digest.settings")
django.setup()


from crypto.utils import CoinManager

mana = CoinManager()
# fee = mana.coin_market_rates()


# print(fee.get('ethereum'))

eth = "0x32bd825f30BA59234c9c3620237f0b14249B109F"
btc= "bc1q4c9hxh36ew6v7yzfflwm03kkc0shcensdz7dzs"
ltc = 'ltc1q7v25d7g2gh0t803tj2u8qy34erl8w92px4ec6e'
xrp = 'rBURNERRhpAM8ygERz7GsXrHRjJrngBLi2'

pr = mana.get_coin_price('eth')

print(pr)