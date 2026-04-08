from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from marketplace.permissions import IsAdminUser

from .models import CustomUser, SellerProfile
from .serializers import SellerProfileSerializer, UserDetailSerializer, UserListSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAdminUser]
    filterset_fields = ["role", "is_active", "is_verified"]
    search_fields = ["username", "email", "phone"]
    ordering_fields = ["date_joined", "username"]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserDetailSerializer

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({"success": True, "id": user.id, "is_active": user.is_active})


class SellerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SellerProfile.objects.select_related("user").all()
    permission_classes = [IsAdminUser]
    serializer_class = SellerProfileSerializer
    filterset_fields = ["is_approved"]
    search_fields = ["shop_name", "user__username"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        seller = self.get_object()
        seller.is_approved = not seller.is_approved
        seller.save()
        return Response({"success": True, "id": seller.id, "is_approved": seller.is_approved})
