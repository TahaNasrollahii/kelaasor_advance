import pytest

pytestmark = pytest.mark.django_db

def test_dashboard_requires_auth(auth_client):
    res = auth_client.get("/api/user_panel/dashboard/")
    assert res.status_code == 200
