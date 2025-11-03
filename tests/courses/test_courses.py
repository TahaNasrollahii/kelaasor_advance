import pytest

pytestmark = pytest.mark.django_db

def test_public_course_list(api_client):
    res = api_client.get("/api/courses/")
    assert res.status_code == 200

def test_public_categories_list(api_client):
    res = api_client.get("/api/courses/categories/")
    assert res.status_code == 200

def test_public_instructors_list(api_client):
    res = api_client.get("/api/courses/instructors/")
    assert res.status_code == 200
