from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from users.models import User
from core.translation import (
    COURSE_TYPE_ONLINE,
    COURSE_TYPE_OFFLINE,
    HELP_COURSE_ACCESS_DURATION,
    HELP_VIDEO_DURATION,
)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')

    def __str__(self):
        return self.name


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="instructor_profile")
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='instructors/', blank=True, null=True)
    expertise = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.full_name or self.user.mobile

class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ("online", COURSE_TYPE_ONLINE),
        ("offline", COURSE_TYPE_OFFLINE),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/images/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructors = models.ManyToManyField(Instructor, related_name='courses')

    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    start_date = models.DateTimeField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)

    access_duration_days = models.PositiveIntegerField(null=True, blank=True, help_text=HELP_COURSE_ACCESS_DURATION)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_registration_open(self):
        """Check if registration is open for online courses."""
        if self.course_type == "online":
            now = timezone.now()
            return self.registration_deadline and now <= self.registration_deadline
        return True

    def __str__(self):
        return self.title


class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Video(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='courses/videos/')
    duration = models.PositiveIntegerField(help_text=HELP_VIDEO_DURATION)
    order = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Attachment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='courses/files/')
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"
