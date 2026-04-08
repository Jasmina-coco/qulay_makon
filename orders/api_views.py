from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from marketplace.permissions import IsAdminUser

from .models import Order
from .serializers import OrderDetailSerializer, OrderListSerializer, OrderStatusSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.select_related("user").prefetch_related("items__product").all()
    permission_classes = [IsAdminUser]
    filterset_fields = ["status", "user"]
    search_fields = ["user__username", "phone", "address"]
    ordering_fields = ["created_at", "total_amount"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderDetailSerializer

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(data=request.data)
        if serializer.is_valid():
            order.status = serializer.validated_data["status"]
            order.save()
            return Response({"success": True, "id": order.id, "status": order.status})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
