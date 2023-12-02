from functools import wraps
from django.http import JsonResponse
import json
import logging

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