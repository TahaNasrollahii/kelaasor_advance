from django.urls import path
from admin_panel.views.users import UserListAPIView, UserDetailAPIView, GroupListAPIView
from admin_panel.views.discounts import DiscountCodeListAPIView, DiscountCodeDetailAPIView
from admin_panel.views.stats import AdminStatsAPIView
from admin_panel.views.notifications import NotificationListAPIView, NotificationMarkReadAPIView
from admin_panel.views.orders import AdminOrderListAPIView, AdminOrderDetailAPIView
from admin_panel.views.tickets import (
    AdminTicketListAPIView,
    AdminTicketDetailAPIView,
    TicketReplyAPIView
)


urlpatterns = [
    # Users & Groups
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<uuid:id>/", UserDetailAPIView.as_view(), name="user-detail"),
    path("groups/", GroupListAPIView.as_view(), name="group-list"),

    # Orders
    path('orders/', AdminOrderListAPIView.as_view(), name='admin-order-list'),
    path('orders/<int:pk>/', AdminOrderDetailAPIView.as_view(), name='admin-order-detail'),

    # Tickets
    path('tickets/', AdminTicketListAPIView.as_view(), name='admin-ticket-list'),
    path('tickets/<int:id>/', AdminTicketDetailAPIView.as_view(), name='admin-ticket-detail'),
    path('tickets/<int:id>/reply/', TicketReplyAPIView.as_view(), name='ticket-reply'),

    # Discounts
    path('discounts/', DiscountCodeListAPIView.as_view(), name='discount-list'),
    path('discounts/<int:id>/', DiscountCodeDetailAPIView.as_view(), name='discount-detail'),

    # Stats
    path('stats/', AdminStatsAPIView.as_view(), name='admin-stats'),

    # Notifications
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications/<int:id>/read/', NotificationMarkReadAPIView.as_view(), name='notification-read'),
]
