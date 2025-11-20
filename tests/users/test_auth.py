import pytest
from django.utils import timezone
from users.models import OTP
from datetime import timedelta

pytestmark = pytest.mark.django_db

def test_send_otp_public(api_client):
    res = api_client.post("/api/users/send-otp/", {"mobile": "+989100000003"}, format="json")
    assert res.status_code in (200, 201)

def test_verify_otp_tokens(api_client):
    # یک OTP معتبر می‌سازیم
    OTP.objects.create(
        mobile="+989100000004",
        code="123456",
        purpose="login",
        is_used=False,
        created_at=timezone.now(),
        expires_at=timezone.now() + timedelta(minutes=5),  # 👈 این خط مهم است
    )
    res = api_client.post("/api/users/verify-otp/", {"mobile": "+989100000004", "code": "123456"}, format="json")
    assert res.status_code == 200
    body = res.json()
    assert "access" in body and "refresh" in body

def test_token_refresh_flow(api_client):
    # قدم اول: ساخت OTP
    OTP.objects.create(
        mobile="+989100000005",
        code="654321",
        purpose="login",
        is_used=False,
        created_at=timezone.now(),
        expires_at=timezone.now() + timedelta(minutes=5),  # 👈 اینجا هم
    )
    # قدم دوم: verify-otp
    res = api_client.post("/api/users/verify-otp/", {"mobile": "+989100000005", "code": "654321"}, format="json")
    assert res.status_code == 200
    refresh = res.json().get("refresh")
    assert refresh

    # قدم سوم: refresh
    res2 = api_client.post("/api/users/token/refresh/", {"refresh": refresh}, format="json")
    assert res2.status_code == 200
    assert "access" in res2.json()
