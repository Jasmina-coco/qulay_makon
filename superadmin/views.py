from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import CustomUser, SellerProfile
from orders.models import Order
from products.models import Category, Product

from .decorators import superadmin_required
from .models import AuditLog, SiteSettings


def superadmin_login(request):
    """Login — faqat superuser"""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("superadmin_main")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            login(request, user)
            AuditLog.log(request, "Super Admin kirdi")
            return redirect("superadmin_main")
        messages.error(request, "Noto'g'ri ma'lumot yoki ruxsat yo'q")
    return render(request, "superadmin/login.html")


def superadmin_logout(request):
    AuditLog.log(request, "Super Admin chiqdi")
    logout(request)
    return redirect("superadmin_login")


@superadmin_required
def superadmin_main(request):
    """ASOSIY SAHIFA — hamma narsa shu yerda"""
    today = timezone.now().date()
    month_start = today.replace(day=1)
    settings = SiteSettings.get_settings()

    context = {
        # Statistika
        "total_users": CustomUser.objects.count(),
        "total_sellers": SellerProfile.objects.count(),
        "total_products": Product.objects.count(),
        "active_products": Product.objects.filter(status="active").count(),
        "pending_products": Product.objects.filter(status="pending").count(),
        "total_orders": Order.objects.count(),
        "pending_orders": Order.objects.filter(status="pending").count(),
        "total_revenue": Order.objects.filter(status="delivered").aggregate(s=Sum("total_amount"))["s"] or 0,
        "total_categories": Category.objects.count(),

        # Adminlar
        "admins": CustomUser.objects.filter(Q(is_superuser=True) | Q(role="admin")).order_by("-date_joined"),
        "all_users": CustomUser.objects.order_by("-date_joined")[:50],

        # Sozlamalar
        "settings": settings,

        # Xatoliklar
        "pending_products_list": Product.objects.filter(status="pending").select_related("category", "seller")[:20],
        "rejected_products_list": Product.objects.filter(status="rejected").select_related("category", "seller")[:20],
        "problem_orders": Order.objects.filter(Q(status="cancelled") | Q(total_amount=0)).select_related("user")[:20],
        "inactive_users": CustomUser.objects.filter(is_active=False)[:20],
        "unapproved_sellers": SellerProfile.objects.filter(is_approved=False).select_related("user")[:20],

        # Log
        "recent_logs": AuditLog.objects.select_related("user")[:30],
    }
    return render(request, "superadmin/main.html", context)


@superadmin_required
def sa_create_admin(request):
    """Yangi admin yaratish"""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        make_super = request.POST.get("is_superuser") == "on"

        if not username or not password:
            messages.error(request, "Username va parol kerak")
            return redirect("superadmin_main")
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, f"{username} allaqachon bor")
            return redirect("superadmin_main")

        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="admin",
            is_staff=True,
            is_superuser=make_super,
            is_verified=True,
        )
        AuditLog.log(request, f"Admin yaratdi: {username}", f"superuser={make_super}")
        messages.success(request, f"{username} yaratildi")
    return redirect("superadmin_main")


@superadmin_required
def sa_delete_admin(request, pk):
    """Admin o'chirish"""
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        return JsonResponse({"error": "O'zingizni o'chira olmaysiz"}, status=400)
    name = user.username
    AuditLog.log(request, f"Admin o'chirdi: {name}")
    user.delete()
    messages.success(request, f"{name} o'chirildi")
    return redirect("superadmin_main")


@superadmin_required
def sa_toggle_user(request, pk):
    """Foydalanuvchini bloklash/ochish"""
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        return JsonResponse({"error": "O'zingizni bloklolmaysiz"}, status=400)
    user.is_active = not user.is_active
    user.save()
    status = "faollashtirildi" if user.is_active else "bloklandi"
    AuditLog.log(request, f"{user.username} {status}")
    messages.success(request, f"{user.username} {status}")
    return redirect("superadmin_main")


@superadmin_required
def sa_save_settings(request):
    """Sozlamalarni saqlash"""
    if request.method == "POST":
        s = SiteSettings.get_settings()
        s.site_name = request.POST.get("site_name", s.site_name)
        s.contact_email = request.POST.get("contact_email", "")
        s.contact_phone = request.POST.get("contact_phone", "")
        s.currency = request.POST.get("currency", "UZS")
        s.commission_percent = request.POST.get("commission_percent", 10)
        s.maintenance_mode = request.POST.get("maintenance_mode") == "on"
        if request.FILES.get("site_logo"):
            s.site_logo = request.FILES["site_logo"]
        s.save()
        AuditLog.log(request, "Sozlamalar yangilandi")
        messages.success(request, "Sozlamalar saqlandi")
    return redirect("superadmin_main")


@superadmin_required
def sa_approve_product(request, pk):
    """Mahsulotni tasdiqlash"""
    product = get_object_or_404(Product, pk=pk)
    product.status = "active"
    product.save()
    AuditLog.log(request, f"Mahsulot tasdiqlandi: {product.name}")
    messages.success(request, f"{product.name} tasdiqlandi")
    return redirect("superadmin_main")


@superadmin_required
def sa_reject_product(request, pk):
    """Mahsulotni rad etish"""
    product = get_object_or_404(Product, pk=pk)
    product.status = "rejected"
    product.save()
    AuditLog.log(request, f"Mahsulot rad etildi: {product.name}")
    messages.success(request, f"{product.name} rad etildi")
    return redirect("superadmin_main")


@superadmin_required
def sa_fix_order(request, pk):
    """Buyurtma statusini tuzatish"""
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get("status")
    if new_status in ["pending", "processing", "shipped", "delivered", "cancelled"]:
        old = order.status
        order.status = new_status
        order.save()
        AuditLog.log(request, f"Buyurtma #{order.id} status: {old} -> {new_status}")
        messages.success(request, f"Buyurtma #{order.id} yangilandi")
    return redirect("superadmin_main")


@superadmin_required
def sa_approve_seller(request, pk):
    """Sotuvchini tasdiqlash"""
    seller = get_object_or_404(SellerProfile, pk=pk)
    seller.is_approved = True
    seller.save()
    AuditLog.log(request, f"Sotuvchi tasdiqlandi: {seller.shop_name}")
    messages.success(request, f"{seller.shop_name} tasdiqlandi")
    return redirect("superadmin_main")


@superadmin_required
def sa_change_user_role(request, pk):
    """Foydalanuvchi rolini o'zgartirish"""
    user = get_object_or_404(CustomUser, pk=pk)
    new_role = request.POST.get("role")
    if new_role in ["admin", "seller", "buyer"]:
        old = user.role
        user.role = new_role
        if new_role == "admin":
            user.is_staff = True
        user.save()
        AuditLog.log(request, f"{user.username} roli: {old} -> {new_role}")
        messages.success(request, f"{user.username} roli o'zgartirildi")
    return redirect("superadmin_main")
