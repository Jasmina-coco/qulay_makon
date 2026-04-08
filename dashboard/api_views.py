from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import CustomUser, SellerProfile
from orders.models import Order
from products.models import Category, Product


@api_view(["GET"])
@permission_classes([AllowAny])
def api_stats(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    return Response(
        {
            "total_users": CustomUser.objects.count(),
            "total_products": Product.objects.filter(status="active").count(),
            "total_orders": Order.objects.count(),
            "total_revenue": float(
                Order.objects.filter(status="delivered").aggregate(s=Sum("total_amount"))["s"]
                or 0
            ),
            "today_orders": Order.objects.filter(created_at__date=today).count(),
            "pending_orders": Order.objects.filter(status="pending").count(),
            "new_users_month": CustomUser.objects.filter(
                date_joined__date__gte=month_start
            ).count(),
            "total_sellers": SellerProfile.objects.count(),
            "total_categories": Category.objects.count(),
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def api_monthly_revenue(request):
    data = (
        Order.objects.filter(status="delivered")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(revenue=Sum("total_amount"))
        .order_by("month")
    )
    return Response(
        [
            {"month": d["month"].strftime("%Y-%m"), "revenue": float(d["revenue"])}
            for d in data
        ]
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def api_order_status_chart(request):
    data = Order.objects.values("status").annotate(count=Count("id"))
    return Response(list(data))


@api_view(["GET"])
@permission_classes([AllowAny])
def api_top_products(request):
    data = (
        Product.objects.filter(status="active")
        .order_by("-views_count")[:10]
        .values("id", "name", "views_count", "price")
    )
    return Response(list(data))
