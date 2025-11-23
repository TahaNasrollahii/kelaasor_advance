import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    User = get_user_model()
    u = User.objects.create_user(
        mobile="+989100000001",
        email="user@example.com",
        full_name="Normal User",
        is_active=True,
        password="P@ssw0rd123"  # اگر پسورد ندارید، مشکلی نیست؛ برای JWT از RefreshToken استفاده می‌کنیم
    )
    return u

@pytest.fixture
def admin_user(db):
    User = get_user_model()
    u = User.objects.create_user(
        mobile="+989100000002",
        email="admin@example.com",
        full_name="Admin User",
        is_active=True,
        is_staff=True,
        is_superuser=True,
        password="P@ssw0rd123"
    )
    return u

@pytest.fixture
def auth_client(api_client, user):
    # مستقیماً از SimpleJWT توکن می‌سازیم (بدون نیاز به لاگین)
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client
