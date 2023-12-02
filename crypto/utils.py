import json
from crypto.models import Coin, Countries
from django.http import JsonResponse
import requests
import logging



logger = logging.getLogger(__name__)



class CoinManager:
    def add_coin(self,network,lable,stable,current_price,coin,token,image,enabled):
        try:
            coin = Coin.objects.create(
                network=network,
                label=lable,
                stable=stable,
                current_price=current_price,
                coin=coin,
                token=token,
                image=image,
                enabled=enabled
            )
            if coin:
                return JsonResponse({"success": True,"info":"Coin added"})
            else:
                return JsonResponse({"success": False,"info":"Unable to add coin"})
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({"success": False,"info":"An error ocurred"})
        
    def add_country(self,name,code,currency):
        try:
            country = Countries.objects.create(
                name=name,
                short_code=code,
                currency=currency
            )
            if country:
                return JsonResponse({"success": True,"info":"country added"})
            else:
                return JsonResponse({"success": False,"info":"Unable to add country"})
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({"success": False,"info":"An error ocurred"})
        
    def get_coin_price(self,coin):
        try:
            api_url = f"https://api.coingecko.com/api/v3/coins/{coin}"
            response = requests.get(api_url)
            data = response.json()
            usd_rate = (
                data.get("market_data", {}).get("current_price", {}).get("usd", 0.0)
            )
            return usd_rate
        except Exception as e:
            logger.warning(f"Error: {str(e)}")
            return JsonResponse(
                {"success": False, "info": "Failed to get exchange rate"}
            )
    
    def coin_market_rates(self):
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 200,
                "page": 1,
                "sparkline": False,
            }
            supported_coins = [
                "btc",
                "usdt",
                "ltc",
                "bch",
                "eth",
                "xrp",
                "dash",
                "usdc",
                "tusd",
            ]

            response = requests.get(url, params=params)
            coin_data = response.json()

            # Filter the coins based on supported symbols
            filtered_coin_data = [
                coin for coin in coin_data if coin["symbol"] in supported_coins
            ]

            return JsonResponse(filtered_coin_data, safe=False)
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({"success": False,"info":"An error ocurred"})