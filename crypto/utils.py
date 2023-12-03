from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
import arrow
from datetime import datetime
from decouple import config
import json
from crypto.models import Coin, Countries
from django.http import JsonResponse
import requests
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class CoinManager:
    # symbol egs btc for bitcoin
    def add_coin(
        self, network, lable, stable, current_price, coin, symbol, image, enabled
    ):
        try:
            coin = Coin.objects.create(
                network=network,
                label=lable,
                stable=stable,
                current_price=current_price,
                coin=coin,
                symbol=symbol,
                image=image,
                enabled=enabled,
            )
            if coin:
                return JsonResponse({"success": True, "info": "Coin added"})
            else:
                return JsonResponse({"success": False, "info": "Unable to add coin"})
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({"success": False, "info": "An error ocurred"})

    def add_country(self, name, code, currency):
        try:
            country = Countries.objects.create(
                name=name, short_code=code, currency=currency
            )
            if country:
                return JsonResponse({"success": True, "info": "country added"})
            else:
                return JsonResponse({"success": False, "info": "Unable to add country"})
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({"success": False, "info": "An error ocurred"})

    def get_coin_price(self, coin):
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
        usd = self.get_coin_price(coin)
        if usd is None:
            raise Exception(f"Exchange rate for {coin} not found in the database")
        rate = Decimal(usd)
        crypto_value = (Decimal(amount_usd) / rate).quantize(
            Decimal("0.00000000"), rounding=ROUND_HALF_UP
        )
        return crypto_value

    def calculate_usd_value(self, crypto_value, coin):
        usd = self.get_coin_price(coin)
        if usd is None:
            raise Exception(f"Exchange rate for {coin} not found in the database")
        rate = Decimal(usd)
        usd_amount = (Decimal(crypto_value) * rate).quantize(
            Decimal("0.00"), rounding=ROUND_DOWN
        )
        return usd_amount

    def transaction_checker(self, coin, address):
        try:
            SATOSHIS_PER_BITCOIN = 100000000

            if coin.lower() in ("btc", "bitcoin"):
                url = f"https://blockchain.info/rawaddr/{address}"
                response = requests.get(url)
                response.raise_for_status()

                data = response.json()

                if "txs" in data:
                    transactions = data["txs"]

                    result = []
                    for transaction in transactions:
                        tx_id = transaction["hash"]

                        if transaction["inputs"][0]["prev_out"]["addr"] == address:
                            sent_or_received = "Sent"
                        else:
                            sent_or_received = "Received"
                        amount_satoshis = abs(transaction["result"])
                        amount_btc = amount_satoshis / SATOSHIS_PER_BITCOIN
                        addr = (
                            transaction["out"][0]["addr"]
                            if sent_or_received == "Received"
                            else transaction["inputs"][0]["prev_out"]["addr"]
                        )
                        usd = self.calculate_usd_value(amount_btc, "bitcoin")
                        timestamp = int(transaction["time"])
                        date_object = datetime.fromtimestamp(timestamp)
                        transaction_info = {
                            "tx_id": tx_id,
                            "type": sent_or_received,
                            "address": addr,
                            "amount_btc": amount_btc,
                            "amount_usd": usd,
                            "date": arrow.get(date_object).format("YYYY-MM-DD"),
                        }

                        result.append(transaction_info)

                    if result:
                        return JsonResponse({"success": True, "data": result})
                    else:
                        return JsonResponse(
                            {"success": False, "info": "No transactions found"}
                        )
                else:
                    logger.warning("No 'txs' found in the API response.")
                    return None

            elif coin == "ethereum" or coin.lower() == "eth":
                api_key_param = {"apikey": config("ETHERSCAN_API_KEY")}
                url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc"

                try:
                    response = requests.get(url, params=api_key_param)
                    response.raise_for_status()

                    data = response.json()

                    if data["status"] == "1":
                        transactions = data["result"]

                        result = []
                        for transaction in transactions:
                            tx_id = transaction["hash"]
                            if transaction["from"] == address:
                                sent_or_received = "Sent"
                            else:
                                sent_or_received = "Received"

                            amount_eth = Decimal(transaction["value"]) / Decimal("1000000000000000000")
                            if sent_or_received == "Received":
                                addr = transaction["from"]
                            else:
                                addr = transaction["to"]
                            usd = self.calculate_usd_value(amount_eth, "ethereum")
                            timestamp = int(transaction["timeStamp"])
                            date_object = datetime.utcfromtimestamp(timestamp)

                            transaction_info = {
                                "tx_id": tx_id,
                                "type": sent_or_received,
                                "address": addr,
                                "amount_eth": amount_eth.quantize(Decimal("0.00000000"), rounding=ROUND_HALF_UP),
                                "amount_usd": usd,
                                "date": date_object.date(),
                            }

                            result.append(transaction_info)

                        if result:
                            return JsonResponse({"success": True, "data": result})
                        else:
                            return JsonResponse(
                                {"success": False, "info": "No transactions found"}
                            )
                    else:
                        return JsonResponse(
                            {"success": False, "info": f"Error: {data['message']}"}
                        )
                except Exception as e:
                    logger.warning(str(e))
                    return JsonResponse({"success": False, "info": "An error ocurred"})

            elif coin.lower() == "ltc" or coin.lower() == "litecoin":
                url = f"https://litecoinspace.org/api/address/{address}/txs"
                try:
                    response = requests.get(url)
                    response.raise_for_status()

                    data = response.json()

                    if data:
                        transactions = data

                        result = []
                        for transaction in transactions:
                            tx_id = transaction.get("txid")
                            sent_or_received = "Sent" if transaction.get("vin")[0]["prevout"]["scriptpubkey_address"] == address else "Received"
                            amount_ltc = Decimal(transaction.get("vout")[0]["value"]) / Decimal("100000000")  # LTC has 8 decimals
                            usd = self.calculate_usd_value(amount_ltc, "litecoin")
                            addr = transaction.get("vout")[0]["scriptpubkey_address"]
                            timestamp = int(transaction["status"]["block_time"])
                            date_object = datetime.utcfromtimestamp(timestamp)

                            transaction_info = {
                                "tx_id": tx_id,
                                "type": sent_or_received,
                                "address": addr,
                                "amount_ltc": amount_ltc.quantize(Decimal("0.00000000"), rounding=ROUND_HALF_UP),
                                "amount_usd": usd,
                                "date": date_object.date(),
                            }

                            result.append(transaction_info)

                        if result:
                            return JsonResponse({"success": True, "data": result})
                        else:
                            return JsonResponse(
                                {"success": False, "info": "No transactions found"}
                            )
                    else:
                        return JsonResponse(
                            {"success": False, "info": "Error: No transaction data found"}
                        )
                except Exception as e:
                    logger.warning(str(e))
                    return JsonResponse({"success": False, "info": "An error occurred"})

            elif coin.lower() == "xrp" or coin.lower() == "ripple":
                url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions"
                try:
                    response = requests.get(url)
                    response.raise_for_status()

                    data = response.json()

                    if data.get("transactions"):
                        transactions = data["transactions"]

                        result = []
                        for transaction in transactions:
                            tx_id = transaction.get("hash")
                            sent_or_received = "Received" if transaction["Destination"] == address else "Sent"
                            amount_xrp = Decimal(transaction["Amount"]["value"]) / Decimal("1000000")  # XRP has 6 decimals
                            usd = self.calculate_usd_value(amount_xrp, "ripple")
                            if sent_or_received == "Sent":
                                addr = transaction["Destination"]
                            else:
                                addr = transaction["Account"]
                            timestamp = datetime.strptime(transaction.get("date"), "%Y-%m-%dT%H:%M:%S.%fZ")

                            transaction_info = {
                                "tx_id": tx_id,
                                "type": sent_or_received,
                                "address": addr,
                                "amount_xrp": amount_xrp.quantize(Decimal("0.000000"), rounding=ROUND_HALF_UP),
                                "amount_usd": usd,
                                "date": timestamp.date(),
                            }

                            result.append(transaction_info)

                        if result:
                            return JsonResponse({"success": True, "data": result})
                        else:
                            return JsonResponse(
                                {"success": False, "info": "No transactions found"}
                            )
                    else:
                        return JsonResponse(
                            {"success": False, "info": "Error: No transaction data found"}
                        )
                except Exception as e:
                    logger.warning(str(e))
                    return JsonResponse({"success": False, "info": "An error occurred"})

        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({"success": False, "info": "An error ocurred"})

