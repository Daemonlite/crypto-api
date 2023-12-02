import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digest.settings")
django.setup()


from crypto.utils import CoinManager

mana = CoinManager()
# fee = mana.coin_market_rates()


# print(fee.get('ethereum'))

eth = "0x95222290dd7278aa3ddd389cc1e1d165cc4bafe51"
my = "bc1q4c9hxh36ew6v7yzfflwm03kkc0shcensdz7dzs"
