from rest_framework import generics, permissions, filters
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from admin_panel.permissions import IsAdmin
from admin_panel.serializers.users import UserListSerializer, UserDetailSerializer, GroupSerializer

User = get_user_model()


class UserListAPIView(generics.ListAPIView):
    """نمایش لیست کاربران با قابلیت جستجو"""
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["date_joined", "username"]


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """مشاهده جزئیات، ویرایش و حذف کاربر"""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    lookup_field = "id"


class GroupListAPIView(generics.ListAPIView):
    """نمایش گروه‌ها برای اختصاص نقش‌ها"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
