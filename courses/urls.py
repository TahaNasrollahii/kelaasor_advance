from django.urls import path
from .views import (
    CategoryListAPIView, CategoryDetailAPIView,
    InstructorListAPIView, InstructorDetailAPIView,
    CourseListAPIView, CourseDetailAPIView,
    ChapterDetailAPIView, VideoDetailAPIView, AttachmentDetailAPIView
)

app_name = "courses"

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailAPIView.as_view(), name='category-detail'),

    path('instructors/', InstructorListAPIView.as_view(), name='instructor-list'),
    path('instructors/<int:pk>/', InstructorDetailAPIView.as_view(), name='instructor-detail'),

    path('', CourseListAPIView.as_view(), name='course-list'),
    path('<slug:slug>/', CourseDetailAPIView.as_view(), name='course-detail'),

    path('chapters/<int:pk>/', ChapterDetailAPIView.as_view(), name='chapter-detail'),
    path('<slug:course_slug>/videos/<int:video_id>/', VideoDetailAPIView.as_view(), name='video-detail'),
    path('attachments/<int:pk>/', AttachmentDetailAPIView.as_view(), name='attachment-detail'),
]
