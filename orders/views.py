import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.views import admin_required
from orders.models import Order


@admin_required
def order_list(request):
    status = request.GET.get("status", "")
    orders = Order.objects.select_related("user").order_by("-created_at")
    if status:
        orders = orders.filter(status=status)
    paginator = Paginator(orders, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "orders/order_list.html", {"page_obj": page_obj, "status": status})


@admin_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.select_related("user").prefetch_related("items__product"), pk=order_id)
    return render(request, "orders/order_detail.html", {"order": order})


@admin_required
@require_POST
def order_update_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    status = request.POST.get("status")
    if not status and request.content_type == "application/json":
        payload = json.loads(request.body.decode("utf-8"))
        status = payload.get("status")
    valid_statuses = {item[0] for item in Order.STATUS_CHOICES}
    if status not in valid_statuses:
        return JsonResponse({"success": False, "message": "Noto'g'ri status."}, status=400)
    order.status = status
    order.save(update_fields=["status"])
    messages.success(request, "Buyurtma statusi yangilandi.")
    return JsonResponse({"success": True, "status": status})


@admin_required
def order_delete(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == "POST":
        order.delete()
        return JsonResponse({"success": True, "message": "Buyurtma o'chirildi"})
    return redirect("order_list")
