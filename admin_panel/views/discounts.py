from rest_framework import generics, filters
from admin_panel.serializers.discounts import DiscountCodeSerializer
from admin_panel.permissions import IsAdminOrProductManager
from purchase.models import DiscountCode


class DiscountCodeListAPIView(generics.ListCreateAPIView):
    """لیست و ایجاد کدهای تخفیف"""
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAdminOrProductManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'description']
    ordering_fields = ['active_from', 'active_until', 'value']
    ordering = ['-active_from']

    def get_queryset(self):
        queryset = DiscountCode.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class DiscountCodeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """مشاهده، ویرایش و حذف کد تخفیف"""
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAdminOrProductManager]
    lookup_field = 'id'
