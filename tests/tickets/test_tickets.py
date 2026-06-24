import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db

def auth_header_for(user):
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}


def test_create_and_reply_ticket(api_client):
    User = get_user_model()
    u = User.objects.create_user(mobile="+989100000007", is_active=True, full_name="Ticket Owner")

    payload = {
        "title": "Registration Issue",
        "status": "open",
        "department": "support",
        "is_public": False
    }

    res_create = api_client.post("/api/tickets/tickets/", payload, format="json", **auth_header_for(u))
    assert res_create.status_code == 201, res_create.content

    ticket_id = res_create.json().get("id")
    assert ticket_id is not None

    res_reply = api_client.post(
        "/api/tickets/tickets/reply/",
        {"ticket": ticket_id, "message": "Thank you for following up"},
        format="json",
        **auth_header_for(u)
    )
    assert res_reply.status_code == 201
