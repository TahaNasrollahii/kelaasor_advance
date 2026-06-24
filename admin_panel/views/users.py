from rest_framework import generics, permissions, filters
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from admin_panel.permissions import IsAdmin
from admin_panel.serializers.users import UserListSerializer, UserDetailSerializer, GroupSerializer

User = get_user_model()


class UserListAPIView(generics.ListAPIView):
    """List users with search capability."""
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["mobile", "email", "full_name"]
    ordering_fields = ["date_joined", "mobile"]


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """View, edit, and soft-delete user details."""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    lookup_field = "id"

    def perform_destroy(self, instance):
        instance.soft_delete()


class GroupListAPIView(generics.ListAPIView):
    """List groups for role assignment."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
