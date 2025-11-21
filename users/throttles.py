from rest_framework.throttling import SimpleRateThrottle

class OTPRateThrottle(SimpleRateThrottle):
    scope = "otp"

    def get_cache_key(self, request, view):
        mobile = request.data.get("mobile")
        if not mobile:
            return None
        return f"throttle_otp_{mobile}"


class OTPVerifyThrottle(SimpleRateThrottle):
    scope = "otp_verify"

    def get_cache_key(self, request, view):
        mobile = request.data.get("mobile")
        if not mobile:
            return None
        return f"otp_verify_{mobile}"