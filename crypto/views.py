import json
from django.http import JsonResponse
from crypto.utils import CoinManager
import logging
logger = logging.getLogger(__name__)
# Create your views here.

manage = CoinManager()

def get_latest_transactions(request):
    try:
        data = json.loads(request.body)
        address = data.get('address')
        coin= data.get('coin')
        man = manage.fetch_latest_transactions(coin, address)
        return man 

    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Unable to fetch request data"})
