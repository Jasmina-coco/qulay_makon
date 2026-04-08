from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import CustomUser, SellerProfile


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.role != "admin" and not request.user.is_superuser:
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return _wrapped


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "/admin-panel/")
            return redirect(next_url)
        messages.error(request, "Username yoki parol noto'g'ri")
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@admin_required
def user_list(request):
    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "").strip()
    users = CustomUser.objects.all().order_by("-date_joined")
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    if role:
        users = users.filter(role=role)
    paginator = Paginator(users, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "accounts/user_list.html",
        {"page_obj": page_obj, "query": query, "role": role},
    )


@admin_required
def user_detail(request, user_id):
    user_obj = get_object_or_404(CustomUser, pk=user_id)
    return render(request, "accounts/user_detail.html", {"user_obj": user_obj})


@admin_required
@require_POST
def user_toggle_active(request, user_id):
    user_obj = get_object_or_404(CustomUser, pk=user_id)
    user_obj.is_active = not user_obj.is_active
    user_obj.save(update_fields=["is_active"])
    return JsonResponse(
        {
            "success": True,
            "is_active": user_obj.is_active,
            "message": "Foydalanuvchi holati yangilandi",
        }
    )


@admin_required
def seller_list(request):
    sellers = SellerProfile.objects.select_related("user").order_by("-created_at")
    paginator = Paginator(sellers, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "accounts/seller_list.html", {"page_obj": page_obj})


@admin_required
@require_POST
def seller_approve(request, seller_id):
    seller = get_object_or_404(SellerProfile, pk=seller_id)
    seller.is_approved = not seller.is_approved
    seller.save(update_fields=["is_approved"])
    return JsonResponse(
        {"success": True, "is_approved": seller.is_approved, "message": "Seller holati yangilandi"}
    )
