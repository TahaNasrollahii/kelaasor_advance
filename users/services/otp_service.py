import json
import random
import redis
from django.conf import settings
from django.core.exceptions import ValidationError

redis_client = redis.Redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))

OTP_TTL = 300  # 5 minutes


def generate_otp(length=6):
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def redis_key(mobile, purpose):
    return f"otp:{purpose}:{mobile}"


def send_otp(mobile, purpose="login"):
    code = generate_otp()

    data = {
        "code": code,
        "purpose": purpose,
    }

    redis_client.setex(redis_key(mobile, purpose), OTP_TTL, json.dumps(data))
    return code


def verify_otp(mobile, code, purpose="login"):
    key = redis_key(mobile, purpose)
    data = redis_client.get(key)

    if not data:
        raise ValidationError("OTP expired or not found.")

    otp = json.loads(data)

    if otp["code"] != code:
        raise ValidationError("Invalid OTP code.")

    # موفقیت → حذف
    redis_client.delete(key)
    return True
