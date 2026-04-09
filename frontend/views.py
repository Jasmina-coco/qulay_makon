from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from dashboard.models import SearchQuery
from products.models import Category, Product

from .models import Banner, ContactMessage, MenuItem, News, Page

try:
    from superadmin.models import SiteSettings
except ImportError:
    SiteSettings = None


def get_site_context():
    ctx = {
        "categories": Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related("children"),
        "menu_items": MenuItem.objects.filter(is_active=True, parent__isnull=True).prefetch_related("children"),
    }
    if SiteSettings:
        ctx["site"] = SiteSettings.get_settings()
    return ctx


def home(request):
    context = get_site_context()
    context.update(
        {
            "banners": Banner.objects.filter(is_active=True),
            "featured_products": Product.objects.filter(status="active", is_featured=True)[:8],
            "new_products": Product.objects.filter(status="active").order_by("-created_at")[:8],
            "popular_products": Product.objects.filter(status="active").order_by("-views_count")[:8],
            "latest_news": News.objects.filter(is_active=True)[:3],
        }
    )
    return render(request, "frontend/home.html", context)


def catalog(request):
    products = Product.objects.filter(status="active").select_related("category").prefetch_related("images")
    category_slug = request.GET.get("category")
    search = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "-created_at")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        cat_ids = [current_category.id] + list(current_category.children.values_list("id", flat=True))
        products = products.filter(category_id__in=cat_ids)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    allowed_sorts = ["-created_at", "created_at", "price", "-price", "-views_count"]
    if sort in allowed_sorts:
        products = products.order_by(sort)

    paginator = Paginator(products, 16)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = get_site_context()
    context.update(
        {
            "products": page_obj,
            "current_category": current_category,
            "search_query": search,
            "current_sort": sort,
        }
    )
    return render(request, "frontend/catalog.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status="active")
    product.views_count += 1
    product.save(update_fields=["views_count"])
    related = Product.objects.filter(category=product.category, status="active").exclude(pk=pk)[:4]
    context = get_site_context()
    context.update({"product": product, "images": product.images.all(), "related_products": related})
    return render(request, "frontend/product_detail.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, status="active").prefetch_related("images")
    paginator = Paginator(products, 16)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = get_site_context()
    context.update({"category": category, "products": page_obj})
    return render(request, "frontend/category.html", context)


def news_list(request):
    articles = News.objects.filter(is_active=True)
    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = get_site_context()
    context["news_list"] = page_obj
    return render(request, "frontend/news_list.html", context)


def news_detail(request, slug):
    article = get_object_or_404(News, slug=slug, is_active=True)
    article.views_count += 1
    article.save(update_fields=["views_count"])
    context = get_site_context()
    context["article"] = article
    return render(request, "frontend/news_detail.html", context)


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    context = get_site_context()
    context["page"] = page
    return render(request, "frontend/page.html", context)


def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name", ""),
            email=request.POST.get("email", ""),
            phone=request.POST.get("phone", ""),
            subject=request.POST.get("subject", ""),
            message=request.POST.get("message", ""),
        )
        return JsonResponse({"success": True, "message": "Xabaringiz yuborildi!"})
    context = get_site_context()
    return render(request, "frontend/contact.html", context)


def search(request):
    q = request.GET.get("q", "").strip()
    products = Product.objects.none()
    if q:
        products = Product.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q), status="active"
        ).prefetch_related("images").order_by("-created_at")
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "127.0.0.1"))
        if "," in ip:
            ip = ip.split(",")[0].strip()
        SearchQuery.objects.create(
            query=q[:300],
            results_count=products.count(),
            ip_address=ip,
        )
    paginator = Paginator(products, 16)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = get_site_context()
    context.update({"products": page_obj, "search_query": q})
    return render(request, "frontend/search.html", context)
