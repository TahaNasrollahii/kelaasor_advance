from django.urls import path
from .views import (
    CartDetailAPIView, CartAddItemAPIView,
    CheckoutAPIView, UserOrdersAPIView,
    ApplyDiscountCodeAPIView, DiscountCodeListAPIView,
)

app_name = "purchase"

urlpatterns = [
    # سبد خرید کاربر
    path('cart/', CartDetailAPIView.as_view(), name='cart-detail'),

    # اضافه کردن دوره به سبد
    path('cart/add/', CartAddItemAPIView.as_view(), name='cart-add-item'),

    # نهایی کردن خرید (checkout)
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),

    # لیست سفارش‌های کاربر
    path('orders/', UserOrdersAPIView.as_view(), name='user-orders'),

    # لیست کد تخفیف ها
    path('discounts/', DiscountCodeListAPIView.as_view(), name='discount-list'),

    # اعمال کد تخفیف
    path('apply-discount/', ApplyDiscountCodeAPIView.as_view(), name='apply-discount'),
]
