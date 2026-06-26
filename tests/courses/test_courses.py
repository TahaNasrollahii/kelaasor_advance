import pytest
from courses.models import Course, Category, Chapter, Video
from purchase.models import Enrollment

pytestmark = pytest.mark.django_db

@pytest.fixture
def course():
    category = Category.objects.create(name="Test Category", slug="test-category")
    c = Course.objects.create(
        title="Test Course",
        slug="test-course",
        category=category,
        price=100000,
        course_type="online",
        is_active=True,
    )
    ch = Chapter.objects.create(course=c, title="Chapter 1", order=1)
    
    # Paid video
    Video.objects.create(chapter=ch, title="Paid Video", duration=60, is_free=False, order=1)
    # Free video
    Video.objects.create(chapter=ch, title="Free Video", duration=30, is_free=True, order=2)
    return c

def test_public_course_endpoints(api_client, course):
    assert api_client.get("/api/courses/").status_code == 200
    assert api_client.get("/api/courses/categories/").status_code == 200
    assert api_client.get("/api/courses/instructors/").status_code == 200

def test_video_access_unenrolled_paid(auth_client, course):
    video = Video.objects.get(is_free=False)
    res = auth_client.get(f"/api/courses/{course.slug}/videos/{video.id}/")
    # Should be forbidden because they are not enrolled and it's not free
    assert res.status_code == 403

def test_video_access_unenrolled_free(auth_client, course):
    video = Video.objects.get(is_free=True)
    res = auth_client.get(f"/api/courses/{course.slug}/videos/{video.id}/")
    # Should be allowed because it's free
    assert res.status_code == 200

def test_video_access_enrolled_paid(auth_client, user, course):
    Enrollment.objects.create(user=user, course=course)
    video = Video.objects.get(is_free=False)
    res = auth_client.get(f"/api/courses/{course.slug}/videos/{video.id}/")
    # Should be allowed because they are enrolled
    assert res.status_code == 200

