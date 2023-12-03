import json
from django.http import JsonResponse
import requests
from crypto.utils import CoinManager
import logging
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)
# Create your views here.

manage = CoinManager()


@csrf_exempt
def get_wallet_transactions(request):
    try:
        data = json.loads(request.body)
        address = data.get("address")
        coin = data.get("coin")
        man = manage.transaction_checker(coin, address)
        return man

    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Unable to fetch request data"})
