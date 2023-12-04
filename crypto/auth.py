import arrow
from django.http import JsonResponse
from crypto.models import Profile
from crypto.notify import Notify
import jwt
from decouple import config
from django.contrib.auth.hashers import make_password, check_password
import random
import logging
from django.contrib.auth import login
from django.core.cache import cache

notify = Notify()
logger = logging.getLogger(__name__)


class Authenticate:
    def generate_token(self, email):
        user = Profile.objects.get(email=email)
        payload = {
            "email": user.email,
            "first_name": user.username,
            "last_name": user.full_name,
            "user_id": str(user.uid),
            "username": user.username,
            "exp": arrow.utcnow().shift(days=7).datetime,
            "iat": arrow.utcnow().datetime,
            "token_type": "refresh",
        }
        return jwt.encode(payload, config("SECRET_KEY"), algorithm="HS256")

    def generate_otp(self):
        # Generate a random 5-digit OTP
        return random.randint(10000, 99999)

    # TODO: set expiry for token
    def send_otp(self, recipient):
        try:
            otp = self.generate_otp()
            context = {
                "email": recipient,
                "template": "otp-verification",
                "context": dict(
                    email=recipient,
                    otp=otp,
                ),
            }
            cache.set(f"{recipient}", otp)
            notify.send_sms_or_email(
                medium="email", recipient=recipient, context=context
            )
            return JsonResponse({"success": True, "info": "OTP sent successfully"})
        except Exception as e:
            logger.warning(f"SMTPException: {str(e)}")
            return JsonResponse(
                {"success": False, "info": "Error sending OTP via email"}
            )

    def verify_otp(self, email, user_entered_otp):
        stored_otp = cache.get(f"{email}")
        logger.warning(stored_otp)
        if stored_otp:
            if int(stored_otp) == int(user_entered_otp):
                user = Profile.objects.get(email=email)
                if user:
                    user.email_verified = True
                    user.save(update_fields=["email_verified"])
                    cache.delete(f"{email}")
                    return JsonResponse(
                        {"success": True, "info": "Email verified successfully"}
                    )

            else:
                return JsonResponse({"success": False, "info": "Invalid OTP"})
        return JsonResponse({"success": False, "info": "OTP expired"})

    def register_user(
        self, username, email, full_name, user_name, phone_number, password
    ):
        try:
            if len(username) < 4 or len(full_name) < 4 or len(user_name) < 4:
                return JsonResponse({"success": False, "info": "input  too short"})

            if len(password) < 8:
                return JsonResponse(
                    {
                        "success": False,
                        "info": "password must contain at least 10 characters",
                    }
                )

            if Profile.objects.filter(email=email):
                return JsonResponse({"success": False, "info": "Email already exists"})

            if Profile.objects.filter(username=username):
                return JsonResponse(
                    {"success": False, "info": "Username already exists"}
                )

            user = Profile.objects.create(
                username=username,
                email=email,
                username=username,
                full_name=full_name,
                phone_number=phone_number,
                password=make_password(password),
            )
            if user:
                self.send_otp(user.email)
                return JsonResponse(
                    {"success": True, "info": "User created successfully"}
                )
            else:
                return JsonResponse(
                    {"success": False, "info": "An error ocurred,try again later"}
                )

        except Exception as e:
            logger.warning(str(e))
            return JsonResponse(
                {"success": False, "info": "An error ocurred,try again later"}
            )

    def login_user(self, email, password, request):
        try:
            user = Profile.objects.get(email=email)

            if not user:
                return JsonResponse(
                    {"success": False, "info": "User with this email does not exist."},
                )

            if check_password(password, user.password):
                if not user.email_verified:
                    return JsonResponse(
                        {"success": False, "info": "Email not verified."}
                    )
                login(request, user)
                access_token = self.generate_token(user.email)

                return JsonResponse(
                    {
                        "success": True,
                        "access_token": access_token,
                    }
                )
            else:
                return JsonResponse(
                    {"success": False, "info": "Invalid email or password."}
                )
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse(
                {"success": False, "info": "Kindly try again --p2prx2--"}
            )

    def get_user_info_from_token(self, token):
        decoded_token = jwt.decode(token, config("SECRET_KEY"), algorithms=["HS256"])
        user_email = decoded_token["email"]

        # Retrieve additional user info using the email
        user = Profile.objects.get(email=user_email)

        # Extract the necessary user info
        user_info = {
            "uid": user.uid,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "username": user.username,
        }

        return user_info
