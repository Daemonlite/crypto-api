import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digest.settings")
django.setup()


from crypto.utils import CoinManager
mana = CoinManager()
fee = mana.calculate_usd_value(0.08288019, 'ethereum')

print(fee)

