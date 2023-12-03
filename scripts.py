import os
import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digest.settings")
django.setup()


from crypto.utils import CoinManager

mana = CoinManager()
# fee = mana.coin_market_rates()


# print(fee.get('ethereum'))

eth = "0x95222290dd7278aa3ddd389cc1e1d165cc4bafe51"
my = "bc1q4c9hxh36ew6v7yzfflwm03kkc0shcensdz7dzs"


url = "https://api.omniexplorer.info/v1/transaction/address"

# Define the form data parameters
data = {"addr": "TRigm6gS7zPntaYBf9N2HoFm2snGaeSpgw", "page": 0}

# Make a POST request to the API
response = requests.post(
    url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}
)
response.raise_for_status()  # Check if the request was successful (status code 200)

# Parse the JSON response
data = response.json()

print(data)
