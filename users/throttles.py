from rest_framework.throttling import SimpleRateThrottle

class OTPRateThrottle(SimpleRateThrottle):
    scope = "otp"

    def get_cache_key(self, request, view):
        mobile = request.data.get("mobile")
        if mobile:
            return f"throttle_otp_{mobile}"
        ip = self.get_ident(request)
        return f"throttle_otp_ip_{ip}"


class OTPVerifyThrottle(SimpleRateThrottle):
    scope = "otp_verify"

    def get_cache_key(self, request, view):
        mobile = request.data.get("mobile")
        if mobile:
            return f"otp_verify_{mobile}"
        ip = self.get_ident(request)
        return f"otp_verify_ip_{ip}"