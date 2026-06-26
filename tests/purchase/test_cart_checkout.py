import pytest
from django.utils import timezone
from datetime import timedelta
from purchase.models import Order, OrderItem, DiscountCode, Enrollment
from courses.models import Course, Category

pytestmark = pytest.mark.django_db

@pytest.fixture
def course():
    category = Category.objects.create(name="Test Category", slug="test-category")
    return Course.objects.create(
        title="Test Course",
        slug="test-course",
        category=category,
        price=100000,
        course_type="online",
        is_active=True,
    )

@pytest.fixture
def discount_code():
    now = timezone.now()
    return DiscountCode.objects.create(
        code="SAVE50",
        discount_type="fixed",
        value=50000,
        active_from=now - timedelta(days=1),
        active_until=now + timedelta(days=1),
        max_usage=1
    )

def test_add_to_cart_and_checkout_success(auth_client, user, course):
    # Add to cart
    res_add = auth_client.post("/api/purchase/cart/add/", {"course": course.id}, format="json")
    assert res_add.status_code == 201

    # Checkout
    res_checkout = auth_client.post("/api/purchase/checkout/", {
        "items": [{
            "course_id": course.id,
            "participants": [{"full_name": "Test Buyer"}]
        }],
        "discount_code": ""
    }, format="json")
    assert res_checkout.status_code == 200
    assert float(res_checkout.json()["total_amount"]) == 100000.0
    
    # Verify enrollment
    assert Enrollment.objects.filter(user=user, course=course).exists()

def test_checkout_empty_cart(auth_client):
    res_checkout = auth_client.post("/api/purchase/checkout/", {
        "items": [],
        "discount_code": ""
    }, format="json")
    
    assert res_checkout.status_code == 400
    assert "items" in res_checkout.json()

def test_checkout_with_exhausted_discount(auth_client, user, course, discount_code):
    discount_code.used_count = 1
    discount_code.save()
    
    auth_client.post("/api/purchase/cart/add/", {"course": course.id}, format="json")
    
    res_checkout = auth_client.post("/api/purchase/checkout/", {
        "items": [{
            "course_id": course.id,
            "participants": [{"full_name": "Test Buyer"}]
        }],
        "discount_code": "SAVE50"
    }, format="json")
    
    assert res_checkout.status_code == 400
    assert "detail" in res_checkout.json()

def test_checkout_missing_participants(auth_client, user, course):
    auth_client.post("/api/purchase/cart/add/", {"course": course.id}, format="json")
    
    res_checkout = auth_client.post("/api/purchase/checkout/", {
        "items": [{
            "course_id": course.id,
            "participants": [] # Missing participants should fail validation
        }],
        "discount_code": ""
    }, format="json")
    
    assert res_checkout.status_code == 400

def test_add_already_purchased_course(auth_client, user, course):
    # Buy it first
    auth_client.post("/api/purchase/cart/add/", {"course": course.id}, format="json")
    auth_client.post("/api/purchase/checkout/", {
        "items": [{"course_id": course.id, "participants": [{"full_name": "Test Buyer"}]}],
        "discount_code": ""
    }, format="json")
    
    # Try adding again
    res_add = auth_client.post("/api/purchase/cart/add/", {"course": course.id}, format="json")
    assert res_add.status_code == 400
    assert "detail" in res_add.json()
