from rest_framework import serializers

from .models import CustomUser, SellerProfile


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "role",
            "is_active",
            "is_verified",
            "date_joined",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "role",
            "avatar",
            "is_active",
            "is_verified",
            "date_joined",
        ]


class SellerProfileSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)

    class Meta:
        model = SellerProfile
        fields = [
            "id",
            "user",
            "shop_name",
            "description",
            "rating",
            "balance",
            "is_approved",
            "created_at",
        ]
