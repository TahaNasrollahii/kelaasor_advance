import pytest
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db

def auth_header_for(user):
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

def test_admin_requires_staff(api_client, user, admin_user):
    r_user = api_client.get("/api/admin-panel/users/", **auth_header_for(user))
    assert r_user.status_code in (401, 403)

    r_admin = api_client.get("/api/admin-panel/users/", **auth_header_for(admin_user))
    assert r_admin.status_code == 200
