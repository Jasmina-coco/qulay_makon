from datetime import timedelta

from django.contrib.postgres.search import SearchQuery as PgSearchQuery
from django.contrib.postgres.search import SearchRank, SearchVector
from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from accounts.models import CustomUser, SellerProfile
from .frontend_forms import BannerForm, NewsForm, PageForm
from .models import SearchQuery, SiteVisit
from frontend.models import Banner, ContactMessage, News, Page
from orders.models import Order, OrderItem
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

    query = PgSearchQuery(query_text)

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


@admin_required
def banner_list(request):
    banners = Banner.objects.all().order_by("order")
    return render(request, "dashboard/banners/list.html", {"banners": banners})


@admin_required
def banner_create(request):
    form = BannerForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("banner_list")
    return render(request, "dashboard/banners/form.html", {"form": form, "title": _("Banner qo'shish")})


@admin_required
def banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    form = BannerForm(request.POST or None, request.FILES or None, instance=banner)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("banner_list")
    return render(request, "dashboard/banners/form.html", {"form": form, "title": _("Banner tahrirlash")})


@admin_required
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == "POST":
        banner.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=405)


@admin_required
def page_list(request):
    pages = Page.objects.all().order_by("-updated_at")
    return render(request, "dashboard/pages/list.html", {"pages": pages})


@admin_required
def page_create(request):
    form = PageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("page_list")
    return render(request, "dashboard/pages/form.html", {"form": form, "title": _("Sahifa qo'shish")})


@admin_required
def page_edit(request, pk):
    page_obj = get_object_or_404(Page, pk=pk)
    form = PageForm(request.POST or None, instance=page_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("page_list")
    return render(request, "dashboard/pages/form.html", {"form": form, "title": _("Sahifa tahrirlash")})


@admin_required
def page_delete(request, pk):
    page_obj = get_object_or_404(Page, pk=pk)
    if request.method == "POST":
        page_obj.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=405)


@admin_required
def news_admin_list(request):
    news = News.objects.select_related("category").all().order_by("-created_at")
    return render(request, "dashboard/news/list.html", {"news_list": news})


@admin_required
def news_create(request):
    form = NewsForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("news_admin_list")
    return render(request, "dashboard/news/form.html", {"form": form, "title": _("Yangilik qo'shish")})


@admin_required
def news_edit(request, pk):
    article = get_object_or_404(News, pk=pk)
    form = NewsForm(request.POST or None, request.FILES or None, instance=article)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("news_admin_list")
    return render(request, "dashboard/news/form.html", {"form": form, "title": _("Yangilik tahrirlash")})


@admin_required
def news_delete(request, pk):
    article = get_object_or_404(News, pk=pk)
    if request.method == "POST":
        article.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=405)


@admin_required
def message_list(request):
    messages_qs = ContactMessage.objects.all().order_by("-created_at")
    return render(request, "dashboard/messages/list.html", {"messages_list": messages_qs})


@admin_required
def message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    return render(request, "dashboard/messages/detail.html", {"message_obj": msg})


@admin_required
def message_mark_read(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save(update_fields=["is_read"])
    return redirect("message_list")


@admin_required
def message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        msg.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=405)


@admin_required
def api_visitors_daily(request):
    thirty_days = timezone.now() - timedelta(days=30)
    data = (
        SiteVisit.objects.filter(created_at__gte=thirty_days)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"), unique=Count("ip_address", distinct=True))
        .order_by("day")
    )
    result = [{"day": d["day"].strftime("%m-%d"), "total": d["total"], "unique": d["unique"]} for d in data]
    return JsonResponse(result, safe=False)


@admin_required
def api_visitors_monthly(request):
    data = (
        SiteVisit.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Count("id"), unique=Count("ip_address", distinct=True))
        .order_by("month")
    )
    result = [
        {"month": d["month"].strftime("%Y-%m"), "total": d["total"], "unique": d["unique"]}
        for d in data
    ]
    return JsonResponse(result, safe=False)


@admin_required
def api_visitors_summary(request):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    return JsonResponse(
        {
            "today_total": SiteVisit.objects.filter(created_at__date=today).count(),
            "today_unique": SiteVisit.objects.filter(created_at__date=today)
            .values("ip_address")
            .distinct()
            .count(),
            "yesterday_total": SiteVisit.objects.filter(created_at__date=yesterday).count(),
            "week_total": SiteVisit.objects.filter(created_at__date__gte=week_ago).count(),
            "week_unique": SiteVisit.objects.filter(created_at__date__gte=week_ago)
            .values("ip_address")
            .distinct()
            .count(),
            "month_total": SiteVisit.objects.filter(created_at__date__gte=month_ago).count(),
            "month_unique": SiteVisit.objects.filter(created_at__date__gte=month_ago)
            .values("ip_address")
            .distinct()
            .count(),
            "all_time": SiteVisit.objects.count(),
        }
    )


@admin_required
def api_top_viewed_products(request):
    data = Product.objects.filter(status="active").order_by("-views_count")[:10].values(
        "id", "name", "views_count", "price", "category__name"
    )
    return JsonResponse(list(data), safe=False)


@admin_required
def api_search_stats(request):
    thirty_days = timezone.now() - timedelta(days=30)
    data = (
        SearchQuery.objects.filter(created_at__gte=thirty_days)
        .values("query")
        .annotate(count=Count("id"), avg_results=Avg("results_count"))
        .order_by("-count")[:15]
    )
    return JsonResponse(list(data), safe=False)


@admin_required
def api_sellers_ranking(request):
    data = (
        OrderItem.objects.filter(order__status="delivered")
        .values(
            "product__seller__id",
            "product__seller__username",
            "product__seller__seller_profile__shop_name",
            "product__seller__seller_profile__rating",
        )
        .annotate(
            total_revenue=Sum(F("price") * F("quantity")),
            total_orders=Count("order", distinct=True),
            total_items=Count("id"),
        )
        .order_by("-total_revenue")[:10]
    )
    result = []
    for d in data:
        result.append(
            {
                "username": d["product__seller__username"],
                "shop_name": d["product__seller__seller_profile__shop_name"]
                or d["product__seller__username"],
                "rating": float(d["product__seller__seller_profile__rating"] or 0),
                "revenue": float(d["total_revenue"] or 0),
                "orders": d["total_orders"],
                "items": d["total_items"],
            }
        )
    return JsonResponse(result, safe=False)


@admin_required
def api_low_stock(request):
    data = (
        Product.objects.filter(status="active", stock__lt=10)
        .order_by("stock")
        .values("id", "name", "stock", "price", "category__name")[:15]
    )
    return JsonResponse(list(data), safe=False)


@admin_required
def api_conversion_rate(request):
    thirty_days = timezone.now() - timedelta(days=30)
    total_visits = SiteVisit.objects.filter(created_at__gte=thirty_days, path__startswith="/product/").count()
    total_orders = Order.objects.filter(created_at__gte=thirty_days).count()
    daily = (
        SiteVisit.objects.filter(created_at__gte=thirty_days, path__startswith="/product/")
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(visits=Count("id"))
        .order_by("day")
    )
    daily_orders = dict(
        Order.objects.filter(created_at__gte=thirty_days)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(orders=Count("id"))
        .values_list("day", "orders")
    )
    chart_data = []
    for d in daily:
        orders = daily_orders.get(d["day"], 0)
        visits = d["visits"] or 1
        chart_data.append(
            {
                "day": d["day"].strftime("%m-%d"),
                "visits": visits,
                "orders": orders,
                "rate": round((orders / visits) * 100, 1) if visits > 0 else 0,
            }
        )
    conversion_rate = round((total_orders / total_visits) * 100, 1) if total_visits > 0 else 0
    return JsonResponse(
        {
            "total_visits": total_visits,
            "total_orders": total_orders,
            "conversion_rate": conversion_rate,
            "daily": chart_data,
        }
    )


@admin_required
def api_recent_activity(request):
    activities = []
    for order in Order.objects.select_related("user").order_by("-created_at")[:5]:
        activities.append(
            {
                "type": "order",
                "icon": "fa-shopping-bag",
                "color": "blue",
                "text": f"{order.user.username} buyurtma berdi (#{order.id})",
                "detail": f"{order.total_amount:,.0f} UZS",
                "time": order.created_at.isoformat(),
            }
        )
    for user in CustomUser.objects.order_by("-date_joined")[:3]:
        activities.append(
            {
                "type": "user",
                "icon": "fa-user-plus",
                "color": "green",
                "text": f"{user.username} ro'yxatdan o'tdi",
                "detail": user.role,
                "time": user.date_joined.isoformat(),
            }
        )
    for product in Product.objects.order_by("-created_at")[:3]:
        activities.append(
            {
                "type": "product",
                "icon": "fa-box",
                "color": "orange",
                "text": f"Yangi mahsulot: {product.name[:30]}",
                "detail": product.get_status_display(),
                "time": product.created_at.isoformat(),
            }
        )
    for visit in SiteVisit.objects.order_by("-created_at")[:4]:
        activities.append(
            {
                "type": "visit",
                "icon": "fa-eye",
                "color": "gray",
                "text": f"Tashrif: {visit.path[:40]}",
                "detail": visit.ip_address,
                "time": visit.created_at.isoformat(),
            }
        )
    activities.sort(key=lambda x: x["time"], reverse=True)
    return JsonResponse(activities[:15], safe=False)
