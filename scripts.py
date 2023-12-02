import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digest.settings")
django.setup()


from crypto.utils import CoinManager

mana = CoinManager()
# fee = mana.coin_market_rates()


# print(fee.get('ethereum'))

from_ = "bc1q8pmuc2v0cku2ty0rfxp2jyvrhv6lpsjzq9y6s8"
my = "bc1q4c9hxh36ew6v7yzfflwm03kkc0shcensdz7dzs"


if my == from_:
    print("yes")
else:
    print("no")
