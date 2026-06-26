import json
import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from core.translation import (
    MSG_REGISTER_SUCCESS, MSG_PASSWORD_MISMATCH, MSG_PHONE_REQUIRED_COUNTRY_CODE,
    MSG_OTP_FORMAT_INVALID, MSG_LOGIN_DEACTIVATED, MSG_IF_ACCOUNT_EXISTS_OTP_SENT,
    MSG_OTP_PASSWORD_RESET, MSG_INVALID_CREDENTIALS
)

User = get_user_model()

pytestmark = pytest.mark.django_db

# --- REGISTRATION TESTS ---

def test_register_success(api_client):
    res = api_client.post("/api/users/register/", {
        "mobile": "+989100000003",
        "full_name": "Test User",
        "password": "StrongPassword123!",
        "password2": "StrongPassword123!"
    }, format="json")
    
    assert res.status_code == 201
    data = res.json()
    assert data["detail"] == MSG_REGISTER_SUCCESS
    assert "access" in data and "refresh" in data
    assert User.objects.filter(mobile="+989100000003").exists()

def test_register_password_mismatch(api_client):
    res = api_client.post("/api/users/register/", {
        "mobile": "+989100000004",
        "password": "StrongPassword123!",
        "password2": "WrongPassword!"
    }, format="json")
    
    assert res.status_code == 400
    assert "password" in res.json()

# --- OTP LOGIN TESTS ---

def test_send_otp_success(api_client):
    with patch("users.services.otp_service.send_otp", return_value="123456"):
        res = api_client.post("/api/users/send-otp/", {
            "mobile": "+989100000005"
        }, format="json")
    assert res.status_code == 200

def test_verify_otp_creates_new_user(api_client, redis_client):
    mobile = "+989100000006"
    redis_client.set(f"otp:login:{mobile}", json.dumps({"code": "123456", "purpose": "login"}), ex=300)

    with patch("users.services.otp_service.redis_client", redis_client):
        res = api_client.post("/api/users/verify-otp/", {
            "mobile": mobile,
            "code": "123456"
        }, format="json")
        
    assert res.status_code == 200
    assert User.objects.filter(mobile=mobile).exists()
    assert "access" in res.json()

def test_verify_otp_invalid_code(api_client, redis_client):
    mobile = "+989100000007"
    # Do not set OTP in redis to simulate invalid/expired
    with patch("users.services.otp_service.redis_client", redis_client):
        res = api_client.post("/api/users/verify-otp/", {
            "mobile": mobile,
            "code": "123456"
        }, format="json")
    
    assert res.status_code == 400

def test_verify_otp_deactivated_user(api_client, redis_client, user):
    user.is_active = False
    user.save()
    
    redis_client.set(f"otp:login:{user.mobile}", json.dumps({"code": "123456", "purpose": "login"}), ex=300)
    with patch("users.services.otp_service.redis_client", redis_client):
        res = api_client.post("/api/users/verify-otp/", {
            "mobile": user.mobile,
            "code": "123456"
        }, format="json")
        
    assert res.status_code == 403
    assert res.json()["detail"] == MSG_LOGIN_DEACTIVATED

# --- PASSWORD RESET TESTS ---

def test_forgot_password_invalid_user(api_client):
    res = api_client.post("/api/users/password/forgot/", {
        "mobile": "+989999999999" # Not existing
    }, format="json")
    assert res.status_code == 400
    assert MSG_IF_ACCOUNT_EXISTS_OTP_SENT in res.json()["mobile"]

def test_forgot_password_success(api_client, user):
    with patch("users.services.otp_service.send_otp", return_value="123456"):
        res = api_client.post("/api/users/password/forgot/", {
            "mobile": user.mobile
        }, format="json")
    assert res.status_code == 200

def test_reset_password_verify_success(api_client, redis_client, user):
    redis_client.set(f"otp:reset_password:{user.mobile}", json.dumps({"code": "123456", "purpose": "reset_password"}), ex=300)
    
    with patch("users.services.otp_service.redis_client", redis_client):
        res = api_client.post("/api/users/password/reset/", {
            "mobile": user.mobile,
            "code": "123456",
            "new_password": "NewStrongPassword123!"
        }, format="json")
        
    assert res.status_code == 200
    assert res.json()["detail"] == MSG_OTP_PASSWORD_RESET
    
    user.refresh_from_db()
    assert user.check_password("NewStrongPassword123!")

