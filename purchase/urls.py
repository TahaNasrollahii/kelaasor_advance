from django.urls import path
from .views import (
    CartDetailAPIView, CartAddItemAPIView,
    CheckoutAPIView, UserOrdersAPIView,
    ApplyDiscountCodeAPIView, DiscountCodeListAPIView,
)

app_name = "purchase"

urlpatterns = [
    path('cart/', CartDetailAPIView.as_view(), name='cart-detail'),

    path('cart/add/', CartAddItemAPIView.as_view(), name='cart-add-item'),

    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),

    path('orders/', UserOrdersAPIView.as_view(), name='user-orders'),

    path('discounts/', DiscountCodeListAPIView.as_view(), name='discount-list'),

    path('apply-discount/', ApplyDiscountCodeAPIView.as_view(), name='apply-discount'),
]
