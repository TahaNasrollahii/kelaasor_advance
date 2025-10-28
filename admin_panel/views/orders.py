from rest_framework import generics, filters
from purchase.models import Order
from admin_panel.serializers.orders import OrderListSerializer, OrderDetailSerializer
from admin_panel.permissions import IsAdminOrSupport


class AdminOrderListAPIView(generics.ListAPIView):
    """
    لیست تمام سفارش‌ها برای ادمین و بخش مالی
    قابلیت فیلتر براساس وضعیت پرداخت و جستجو بر اساس نام کاربر
    """
    serializer_class = OrderListSerializer
    permission_classes = [IsAdminOrSupport]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__mobile', 'user__email', 'user__full_name']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Order.objects.all().select_related('user').prefetch_related('items')
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


class AdminOrderDetailAPIView(generics.RetrieveAPIView):
    """
    مشاهده جزئیات یک سفارش خاص
    """
    queryset = Order.objects.all().select_related('user').prefetch_related('items__course')
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminOrSupport]
