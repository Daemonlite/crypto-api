import json
from django.http import JsonResponse
from crypto.utils import CoinManager
from django.views.decorators.csrf import csrf_exempt
from crypto.decorators import check_fields, token_required
from crypto.auth import Authenticate
from django.contrib.auth import logout
from crypto.models import Profile
from django.views.decorators.http import require_POST, require_GET

import logging

logger = logging.getLogger(__name__)
# Create your views here.

manage = CoinManager()
auth = Authenticate()


@check_fields(
    ["username", "email", "full_name", "username", "phone_number", "password"]
)
@csrf_exempt
@require_POST
def register_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        full_name = data.get("full_name")
        username = data.get("username")
        phone_number = data.get("phone_number")
        password = data.get("password")
        reg = auth.register_user(
            username, email, full_name, phone_number, password
        )
        return reg
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Kindly try again --p2prx2--"})


@check_fields(["email", "password"])
@csrf_exempt
@require_POST
def login_user(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        log = auth.login_user(email, password, request)
        return log
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Kindly try again --p2prx2--"})


@check_fields(["email", "otp_code"])
@csrf_exempt
@require_POST
def verify_email(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        otp_code = data.get("otp_code")

        return auth.verify_otp(
            email,
            otp_code,
        )
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Kindly try again --p2prx2--"})


@check_fields(["email"])
@csrf_exempt
@require_POST
def resend_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        return auth.resend_otp(email)
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Kindly try again --p2prx2--"})


@token_required
@require_GET
def get_profiles(request):
    try:
        profiles = Profile.objects.all()
        return JsonResponse({"success": True, "data": list(profiles.values())})
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Kindly try again --p2prx2--"})


@require_POST
@csrf_exempt
@token_required
def logout_user(request):
    logout(request)
    return JsonResponse({"success": True, "info": "Logged out successfully."})


@csrf_exempt
@require_POST
@token_required
@check_fields(["coin", "user_id"])
def add_coin(request):
    try:
        data = json.loads(request.body)
        coin = data.get("coin")
        user_id = data.get("user_id")
        man = manage.add_coin(user_id, coin)
        return man
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Unable to fetch request data"})


@csrf_exempt
@require_POST
@token_required
@check_fields(["address", "user_id", "name"])
def add_wallet_address(request):
    try:
        data = json.loads(request.body)
        address = data.get("address")
        user_id = data.get("user_id")
        name = data.get("name")
        identifier = data.get("identifier")
        man = manage.add_wallet_address(user_id, address, name, identifier)
        return man
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Unable to fetch request data"})


@require_GET
@token_required
@check_fields(["user_id", "identifier", "coin_name"])
def fetch_address_identifier(request):
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        identifier = data.get("identifier")
        coin_name = data.get("coin_name")
        man = manage.get_user_wallet(user_id, identifier, coin_name)
        return man
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Kindly try again --p2prx2--"})


@require_GET
@token_required
@check_fields(["user_id"])
def get_user_coins(request):
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        coins = manage.get_coins(user_id)
        return coins
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Kindly try again --p2prx2--"})


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


@require_GET
@token_required
@check_fields(["user_id", "coin", "identifier"])
def check_balance(request):
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        coin = data.get("coin")
        identifier = data.get("identifier")

        bal = manage.user_wallet_balance(user_id, coin, identifier)
        return bal
    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Kindly try again --p2prx2--"})


@require_GET
@token_required
@check_fields(["coin", "user_id", "identifier"])
def check_transactions(request):
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        coin = data.get("coin")
        identifier = data.get("identifier")
        transact = manage.get_user_wallet_transactions(user_id, coin, identifier)
        return transact

    except Exception as e:
        logger.warning(str(e))
        return JsonResponse({"success": False, "info": "Kindly try again --p2prx2--"})
