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
            username, email, full_name, username, phone_number, password
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
