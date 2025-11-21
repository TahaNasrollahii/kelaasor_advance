from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
import uuid
import random

from django.utils import timezone

PHONE_RE = RegexValidator(
    regex=r'^\+?989\d{9}$',
    message='Phone number must be: +989XXXXXXXXX or 989XXXXXXXXX'
)


class UserManager(BaseUserManager):
    def create_user(self, mobile, password=None, full_name=None, email=None, **extra_fields):
        if not mobile:
            raise ValueError("Mobile number is required")
        mobile = str(mobile).strip()
        user = self.model(mobile=mobile, full_name=full_name or '', email=email or '', **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not password:
            raise ValueError("Superuser must have a password.")
        return self.create_user(mobile=mobile, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses mobile as USERNAME_FIELD.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mobile = models.CharField(max_length=15, unique=True, validators=[PHONE_RE], db_index=True)
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['mobile']),
            models.Index(fields=['is_instructor']),
        ]

    def __str__(self):
        return self.mobile

    def soft_delete(self):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['deleted', 'deleted_at', 'is_active'])


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=True, blank=True)
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"

    def __str__(self):
        return f"Profile of {self.user.mobile}"



class TeamEnrollment(models.Model):
    """
    A temporary container for group purchase members.
    - buyer: the user who creates the group purchase
    - course: which course is being bought (nullable for initial)
    - reference_id: optional client-provided ID to relate to cart/order
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_enrollments')
    course_slug = models.CharField(max_length=320, blank=True, help_text="Optional course slug to lock members to one course")
    reference_id = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TeamMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(TeamEnrollment, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=15, validators=[PHONE_RE], blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name='as_team_member')  # if member is existing user
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['email']), models.Index(fields=['mobile'])]


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title