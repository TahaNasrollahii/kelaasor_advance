from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import Category, Instructor, Course, Chapter, Video, Attachment
from .serializers import (
    CategorySerializer, InstructorSerializer,
    CourseListSerializer, CourseDetailSerializer,
    ChapterSerializer, VideoSerializer, AttachmentSerializer
)
from .permissions import IsEnrolledOrVideoIsFree


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


class InstructorListAPIView(generics.ListAPIView):
    queryset = Instructor.objects.select_related('user').all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.AllowAny]

class InstructorDetailAPIView(generics.RetrieveAPIView):
    queryset = Instructor.objects.select_related('user').all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.AllowAny]


class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.filter(is_active=True).select_related('category').prefetch_related('instructors')
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]

class CourseDetailAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_active=True).select_related('category').prefetch_related('instructors','chapters__videos','attachments')
    serializer_class = CourseDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


class ChapterDetailAPIView(generics.RetrieveAPIView):
    queryset = Chapter.objects.prefetch_related('videos').all()
    serializer_class = ChapterSerializer
    permission_classes = [permissions.AllowAny]


class VideoDetailAPIView(generics.RetrieveAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsEnrolledOrVideoIsFree]

    def get_object(self):
        course_slug = self.kwargs.get("course_slug")
        video_id = self.kwargs.get("video_id")
        return get_object_or_404(
            Video.objects.select_related("chapter__course"),
            id=video_id,
            chapter__course__slug=course_slug
        )


class AttachmentDetailAPIView(generics.RetrieveAPIView):
    queryset = Attachment.objects.select_related('course').all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
