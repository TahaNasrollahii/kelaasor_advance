from django.urls import path
from admin_panel.views.discounts import DiscountCodeListAPIView, DiscountCodeDetailAPIView
from admin_panel.views.users import UserListAPIView, UserDetailAPIView, GroupListAPIView


app_name = "admin_panel"

urlpatterns = [
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:id>/", UserDetailAPIView.as_view(), name="user-detail"),
    path("groups/", GroupListAPIView.as_view(), name="group-list"),

    path('discounts/', DiscountCodeListAPIView.as_view(), name='discount-list'),
    path('discounts/<int:id>/', DiscountCodeDetailAPIView.as_view(), name='discount-detail'),
]
