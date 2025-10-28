from rest_framework import serializers
from django.contrib.auth import get_user_model, models as auth_models

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.Group
        fields = ["id", "name"]


class UserListSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "mobile", "email", "full_name", "is_active", "groups", "date_joined"]


class UserDetailSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "date_joined",
            "last_login",
        ]

    def update(self, instance, validated_data):
        groups_data = validated_data.pop("groups", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if groups_data:
            group_objs = [auth_models.Group.objects.get(name=g["name"]) for g in groups_data]
            instance.groups.set(group_objs)
        return instance
