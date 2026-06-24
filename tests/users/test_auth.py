import json
import pytest
from unittest.mock import patch

pytestmark = pytest.mark.django_db

def test_send_otp_public(api_client):
    with patch("users.services.otp_service.send_otp", return_value="123456"):
        res = api_client.post("/api/users/send-otp/", {
            "mobile": "+989100000003"
        }, format="json")

    assert res.status_code == 200
    assert res.json()["detail"] == "OTP sent successfully."

def test_verify_otp_tokens(api_client, redis_client):
    mobile = "+989100000004"

    redis_client.set(
        f"otp:login:{mobile}",
        json.dumps({"code": "123456", "purpose": "login"}),
        ex=300
    )

    with patch("users.services.otp_service.redis_client", redis_client):
        res = api_client.post("/api/users/verify-otp/", {
            "mobile": mobile,
            "code": "123456"
        }, format="json")

    assert res.status_code == 200
    data = res.json()
    assert "access" in data and "refresh" in data


def test_token_refresh_flow(api_client, redis_client):
    mobile = "+989100000005"

    redis_client.set(
        f"otp:login:{mobile}",
        json.dumps({"code": "654321", "purpose": "login"}),
        ex=300
    )

    with patch("users.services.otp_service.redis_client", redis_client):
        res = api_client.post("/api/users/verify-otp/", {
            "mobile": mobile,
            "code": "654321"
        }, format="json")

    assert res.status_code == 200
    refresh = res.json().get("refresh")
    assert refresh is not None

    res2 = api_client.post("/api/users/token/refresh/", {"refresh": refresh})
    assert res2.status_code == 200
    assert "access" in res2.json()
