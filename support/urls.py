from django.urls import path
from .views import (
    TicketListCreateAPIView,
    TicketRetrieveUpdateAPIView,
    TicketReplyCreateAPIView
)


urlpatterns = [
    path('tickets/', TicketListCreateAPIView.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', TicketRetrieveUpdateAPIView.as_view(), name='ticket-detail-update'),
    path('tickets/reply/', TicketReplyCreateAPIView.as_view(), name='ticket-reply-create'),
]
