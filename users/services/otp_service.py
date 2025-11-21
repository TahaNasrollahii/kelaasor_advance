import json
import random
import time
from django.conf import settings
from django.core.exceptions import ValidationError
import redis


# اتصال Redis
redis_client = redis.Redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))

OTP_TTL = 300             # 5 دقیقه
LOCK_MINUTES = 15         # بعد از 5 تلاش اشتباه
MAX_ATTEMPTS = 5          # تعداد مجاز وارد کردن کد


def generate_otp(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def redis_key(mobile, purpose):
    return f"otp:{purpose}:{mobile}"


def send_otp(mobile, purpose="login"):
    key = redis_key(mobile, purpose)

    otp_data = {
        "code": generate_otp(),
        "attempts": 0,
        "purpose": purpose,
        "locked_until": 0
    }

    # ذخیره در Redis به‌صورت JSON
    redis_client.setex(key, OTP_TTL, json.dumps(otp_data))

    return otp_data["code"]


def verify_otp(mobile, code, purpose="login"):
    key = redis_key(mobile, purpose)
    data = redis_client.get(key)

    if not data:
        raise ValidationError("OTP expired or not found.")

    otp = json.loads(data)

    # بررسی قفل
    now_ts = int(time.time())
    if otp["locked_until"] > now_ts:
        raise ValidationError("Too many attempts, try again later.")

    # مقایسه کد
    if otp["code"] != code:
        otp["attempts"] += 1

        # قفل کردن در صورت تلاش بیش از حد
        if otp["attempts"] >= MAX_ATTEMPTS:
            otp["locked_until"] = now_ts + LOCK_MINUTES * 60

        # ذخیره مجدد
        redis_client.setex(key, OTP_TTL, json.dumps(otp))
        raise ValidationError("Invalid OTP code.")

    # موفقیت: حذف OTP از Redis
    redis_client.delete(key)
    return True
