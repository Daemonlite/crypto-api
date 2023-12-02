import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digest.settings")
django.setup()


from crypto.utils import CoinManager
mana = CoinManager()
fee = mana.get_coin_price('bitcoin')

print(fee)

