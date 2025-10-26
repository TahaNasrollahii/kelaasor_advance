from rest_framework import serializers
from purchase.models import DiscountCode


class DiscountCodeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = DiscountCode
        fields = [
            'id',
            'code',
            'description',
            'discount_type',
            'value',
            'active_from',
            'active_until',
            'max_usage',
            'used_count',
            'user',
            'user_username',
            'course',
            'course_title',
            'is_active',
        ]
