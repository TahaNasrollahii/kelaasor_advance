import pytest
from django.contrib.auth import get_user_model
from ticket.models import Ticket, TicketMessage

pytestmark = pytest.mark.django_db

User = get_user_model()

@pytest.fixture
def other_user():
    return User.objects.create_user(mobile="+989100000009", is_active=True, full_name="Other")

@pytest.fixture
def private_ticket(user):
    return Ticket.objects.create(
        title="Private Issue", status="open", department="support", is_public=False, user=user
    )

@pytest.fixture
def public_ticket(user):
    return Ticket.objects.create(
        title="Public Issue", status="open", department="support", is_public=True, user=user
    )

def test_create_and_reply_ticket_success(auth_client, user):
    payload = {
        "title": "Registration Issue",
        "status": "open",
        "department": "support",
        "is_public": False
    }

    res_create = auth_client.post("/api/tickets/tickets/", payload, format="json")
    assert res_create.status_code == 201

    ticket_id = res_create.json().get("id")
    
    res_reply = auth_client.post(
        "/api/tickets/tickets/reply/",
        {"ticket": ticket_id, "message": "Thank you for following up"},
        format="json"
    )
    assert res_reply.status_code == 201

def test_cannot_access_others_private_ticket(api_client, other_user, private_ticket):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(other_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    
    res = api_client.get(f"/api/tickets/tickets/{private_ticket.id}/")
    assert res.status_code == 404 # DRF returns 404 for objects outside of queryset usually, or 403

def test_can_access_others_public_ticket(api_client, other_user, public_ticket):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(other_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    
    res = api_client.get(f"/api/tickets/tickets/{public_ticket.id}/")
    assert res.status_code == 200
