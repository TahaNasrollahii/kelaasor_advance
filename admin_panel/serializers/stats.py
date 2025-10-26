from rest_framework import serializers

class StatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_tickets_open = serializers.IntegerField()
    total_tickets_in_progress = serializers.IntegerField()
    total_tickets_closed = serializers.IntegerField()
    total_discount_codes_active = serializers.IntegerField()
