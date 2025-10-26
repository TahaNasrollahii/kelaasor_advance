from django.urls import path
from admin_panel.views.users import UserListAPIView, UserDetailAPIView, GroupListAPIView


app_name = "admin_panel"

urlpatterns = [
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:id>/", UserDetailAPIView.as_view(), name="user-detail"),
    path("groups/", GroupListAPIView.as_view(), name="group-list"),
]
