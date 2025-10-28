from django.urls import path
from .views import (
    TicketListCreateAPIView,
    TicketRetrieveUpdateAPIView,
    TicketMessageCreateAPIView
)

app_name = "ticket"

urlpatterns = [
    path('tickets/', TicketListCreateAPIView.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', TicketRetrieveUpdateAPIView.as_view(), name='ticket-detail-update'),
    path('tickets/reply/', TicketMessageCreateAPIView.as_view(), name='ticket-reply-create'),
]
