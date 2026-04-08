from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUser, SellerProfile
from orders.models import Order
from products.models import Category, Product
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.role != "admin" and not request.user.is_superuser:
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return _wrapped


@admin_required
def dashboard_view(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    context = {
        "total_users": CustomUser.objects.count(),
        "total_products": Product.objects.count(),
        "active_products": Product.objects.filter(status="active").count(),
        "total_orders": Order.objects.count(),
        "total_revenue": Order.objects.filter(status="delivered").aggregate(s=Sum("total_amount"))["s"] or 0,
        "today_orders": Order.objects.filter(created_at__date=today).count(),
        "pending_orders": Order.objects.filter(status="pending").count(),
        "new_users_month": CustomUser.objects.filter(date_joined__date__gte=month_start).count(),
        "total_sellers": SellerProfile.objects.count(),
        "total_categories": Category.objects.count(),
        "recent_orders": Order.objects.select_related("user").order_by("-created_at")[:10],
        "recent_users": CustomUser.objects.order_by("-date_joined")[:5],
    }
    return render(request, "dashboard/index.html", context)


@admin_required
def api_monthly_revenue(request):
    data = (
        Order.objects.filter(status="delivered")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(revenue=Sum("total_amount"))
        .order_by("month")
    )
    result = [{"month": d["month"].strftime("%Y-%m"), "revenue": float(d["revenue"])} for d in data]
    return JsonResponse(result, safe=False)


@admin_required
def api_order_status_chart(request):
    data = Order.objects.values("status").annotate(count=Count("id"))
    return JsonResponse(list(data), safe=False)


@admin_required
def api_top_products(request):
    data = Product.objects.order_by("-views_count")[:10].values("name", "views_count")
    return JsonResponse(list(data), safe=False)


@admin_required
def api_dashboard_stats(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    stats = {
        "total_users": CustomUser.objects.count(),
        "total_products": Product.objects.filter(status="active").count(),
        "total_orders": Order.objects.count(),
        "total_revenue": float(
            Order.objects.filter(status="delivered").aggregate(s=Sum("total_amount"))["s"]
            or 0
        ),
        "today_orders": Order.objects.filter(created_at__date=today).count(),
        "new_users_month": CustomUser.objects.filter(date_joined__date__gte=month_start).count(),
    }
    return JsonResponse(stats)


@admin_required
def api_global_search(request):
    query_text = request.GET.get("q", "").strip()
    if len(query_text) < 2:
        return JsonResponse({"results": []})

    query = SearchQuery(query_text)

    products = (
        Product.objects.annotate(
            search=SearchVector("name", weight="A") + SearchVector("description", weight="B"),
            rank=SearchRank(SearchVector("name", weight="A") + SearchVector("description", weight="B"), query),
        )
        .filter(search=query)
        .select_related("category")
        .order_by("-rank")[:5]
    )
    users = (
        CustomUser.objects.annotate(
            search=SearchVector("username", weight="A") + SearchVector("email", weight="B"),
            rank=SearchRank(SearchVector("username", weight="A") + SearchVector("email", weight="B"), query),
        )
        .filter(search=query)
        .order_by("-rank")[:5]
    )
    orders = (
        Order.objects.annotate(
            search=SearchVector("address", weight="A") + SearchVector("phone", weight="B"),
            rank=SearchRank(SearchVector("address", weight="A") + SearchVector("phone", weight="B"), query),
        )
        .filter(search=query)
        .select_related("user")
        .order_by("-rank")[:5]
    )

    results = []
    for item in products:
        results.append(
            {
                "type": "product",
                "title": item.name,
                "subtitle": f"{item.category.name if item.category else '-'} | {item.status}",
                "url": reverse("product_detail", args=[item.id]),
            }
        )
    for item in users:
        results.append(
            {
                "type": "user",
                "title": item.username,
                "subtitle": item.email or item.role,
                "url": reverse("user_detail", args=[item.id]),
            }
        )
    for item in orders:
        results.append(
            {
                "type": "order",
                "title": f"Order #{item.id}",
                "subtitle": f"{item.user.username} | {item.status}",
                "url": reverse("order_detail", args=[item.id]),
            }
        )

    return JsonResponse({"results": results[:12]})
