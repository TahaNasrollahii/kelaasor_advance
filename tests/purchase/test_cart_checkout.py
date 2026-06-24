import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from courses.models import Course, Category

pytestmark = pytest.mark.django_db

def auth_header_for(user):
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

def test_add_to_cart_and_checkout(api_client):
    User = get_user_model()
    user = User.objects.create_user(mobile="+989100000006", is_active=True, full_name="Buyer")

    category = Category.objects.create(name="Test Category", slug="test-category")
    course = Course.objects.create(
        title="Test Course",
        slug="test-course",
        category=category,
        price=100000,
        course_type="online",
        is_active=True,
    )

    res_add = api_client.post("/api/purchase/cart/add/", {"course": course.id}, format="json", **auth_header_for(user))
    assert res_add.status_code == 201

    res_cart = api_client.get("/api/purchase/cart/", **auth_header_for(user))
    assert res_cart.status_code == 200
    assert len(res_cart.json()["items"]) == 1

    res_checkout = api_client.post("/api/purchase/checkout/", {
        "items": [{
            "course_id": course.id,
            "participants": [{"full_name": "Test Buyer"}]
        }],
        "discount_code": ""
    }, format="json", **auth_header_for(user))
    assert res_checkout.status_code == 200
    assert res_checkout.json()["total_amount"] == "100000.00"
