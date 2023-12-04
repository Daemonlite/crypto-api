from functools import wraps
import arrow
from django.http import JsonResponse
import json
import logging
from decouple import config
import jwt

logger = logging.getLogger(__name__)


def check_fields(required_fields):
    def checker(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.method in ["POST", "GET"]:
                try:
                    request_data = json.loads(request.body)
                except Exception as e:
                    logger.warning(str(e))
                    return JsonResponse(
                        {"success": False, "info": "Unable to fetch request data"}
                    )
            else:
                return JsonResponse(
                    {"success": False, "info": "Request method is not allowed"}
                )
                # Check if the required fields are present and not empty in the request data.
            for field in required_fields:
                if field not in request_data or not request_data[field]:
                    return JsonResponse(
                        {
                            "success": False,
                            "info": f"{field} is required and cannot be empty",
                        }
                    )

            return view_func(request, *args, **kwargs)

        return wrapped_view

    return checker


def token_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        access_token = request.headers.get("Authorization")

        if not access_token:
            return JsonResponse({"error": "Access token is missing."}, status=401)

        try:
            decoded_token = jwt.decode(
                access_token, config("SECRET_KEY"), algorithms=["HS256"]
            )

            expiration_time = arrow.get(decoded_token["exp"])
            logger.warning(expiration_time)
            token_type = decoded_token.get("token_type")

            if token_type not in ["access", "refresh"]:
                return JsonResponse(
                    {"error": "Invalid access token passed."}, status=401
                )

        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"error": "Access token has already expired."}, status=401
            )
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token:", str(e))
            return JsonResponse({"error": "Invalid access token."}, status=401)

        return func(request, *args, **kwargs)

    return wrapper
