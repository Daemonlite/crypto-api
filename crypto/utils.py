from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from decouple import config
import json
from crypto.models import Coin, Countries
from django.http import JsonResponse
import requests
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)



class CoinManager:
    #symbol egs btc for bitcoin
    def add_coin(self,network,lable,stable,current_price,coin,symbol,image,enabled):
        try:
            coin = Coin.objects.create(
                network=network,
                label=lable,
                stable=stable,
                current_price=current_price,
                coin=coin,
                symbol=symbol,
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
            # Make a request to the CoinGecko API to get coin data in USD
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
            response.raise_for_status()
            coin_data = response.json()
    
            # Filter the coin data based on supported symbols
            coins = [
                (coin["id"], coin["current_price"])
                for coin in coin_data
                if coin["symbol"] in supported_coins
            ]
            return coins
    
        except Exception as e:
            logger.warning(str(e))
            return {}

    
    def convert_currency(self, to, amount):
            url = f"https://api.apilayer.com/fixer/convert?to={to}&from=USD&amount={amount}"
            payload = {}
            headers = {
                "apikey": config("FIXER_KEY"),
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()
            amount = result["result"]
            form = f"{amount:.2f}"
            return form
    

    
    def calculate_crypto_value(self, amount_usd, coin):
            rates = dict(self.coin_market_rates())  
            usd = rates.get(coin)
            if usd is None:
                raise Exception(f"Exchange rate for {coin} not found in the database")
            rate = Decimal(usd)
            crypto_value = (Decimal(amount_usd) / rate).quantize(
                Decimal("0.00000000"), rounding=ROUND_HALF_UP
            )
            return crypto_value
    
    def calculate_usd_value(self, crypto_value, coin):
        rates = dict(self.coin_market_rates())  
        usd = rates.get(coin)
        if usd is None:
            raise Exception(f"Exchange rate for {coin} not found in the database")
        rate = Decimal(usd)
        usd_amount = (Decimal(crypto_value) * rate).quantize(
            Decimal("0.00"), rounding=ROUND_DOWN
        )
        return usd_amount



    def fetch_latest_transactions(self, coin, address):
        try:
            SATOSHIS_PER_BITCOIN = 100000000
            if coin.lower() in ('btc', 'bitcoin'):
                url = f"https://blockchain.info/rawaddr/{address}"
                response = requests.get(url)
                response.raise_for_status()  # Check if the request was successful (status code 200)

                data = response.json()

                if 'txs' in data:
                    transactions = data['txs'][:5]  # Get the last 5 transactions

                    result = []
                    for transaction in transactions:
                        tx_id = transaction['hash']
                        sent_or_received = 'Sent' if transaction['result'] < 0 else 'Received'
                        amount_satoshis = abs(transaction['result'])
                        amount_btc = amount_satoshis / SATOSHIS_PER_BITCOIN
                        addr = transaction['out'][0]['addr'] if sent_or_received == 'Received' else transaction['inputs'][0]['prev_out']['addr']

                        transaction_info = {
                            'tx_id': tx_id,
                            'type': sent_or_received,
                            'address': addr,
                            'amount_btc': amount_btc
                        }

                        result.append(transaction_info)

                    if result:
                        return JsonResponse({"success": True, "data": result})
                    else:
                        return JsonResponse({"success": False, "info": "No transactions found"})
                else:
                    logger.warning("No 'txs' found in the API response.")
                    return None
            
            if coin == "ethereum" or "eth":
                api_key_param = {'apikey': config("ETHERSCAN_API_KEY")}
    
                # Replace 'address' with the Ethereum address you want to check
                url = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc'

                try:
                    response = requests.get(url, params=api_key_param)
                    response.raise_for_status()  # Check if the request was successful (status code 200)

                    data = response.json()

                    if data['status'] == '1':
                        transactions = data['result'][:5]  # Get the last 5 transactions

                        result = []
                        for transaction in transactions:
                            tx_id = transaction['hash']
                            sent_or_received = 'Sent' if Decimal(transaction['value']) < 0 else 'Received'
                            amount_eth = Decimal(transaction['value']) / Decimal('1000000000000000000')
                            addr = transaction['from'] if sent_or_received == 'Received' else transaction['to']

                            transaction_info = {
                                'tx_id': tx_id,
                                'type': sent_or_received,
                                'address': addr,
                                'amount_eth': amount_eth.quantize(Decimal('0.00000000'), rounding=ROUND_HALF_UP)
                            }

                            result.append(transaction_info)

                        if result:
                            return JsonResponse({"success": True, "data": result})
                        else:
                            return {"success": False, "info": "No transactions found"}
                    else:
                        return {"success": False, "info": f"Error: {data['message']}"}
                except Exception as e:
                    logger.warning(str(e))
                    return JsonResponse({"success": False, "info": "An error ocurred"})

        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({"success": False, "info": "An error ocurred"})