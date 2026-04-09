from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from import_export.formats.base_formats import CSV, XLSX

from accounts.models import CustomUser
from accounts.views import admin_required
from products.forms import CategoryForm, ProductForm
from products.models import Category, Product, ProductImage
from products.resources import CategoryResource, ProductResource


@admin_required
def product_list(request):
    query = request.GET.get("q", "")
    status = request.GET.get("status", "")
    category_id = request.GET.get("category", "")
    products = Product.objects.select_related("seller", "category").order_by("-created_at")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if status:
        products = products.filter(status=status)
    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    categories = Category.objects.filter(is_active=True)
    context = {
        "page_obj": page_obj,
        "categories": categories,
        "query": query,
        "status": status,
        "category_id": category_id,
    }
    return render(request, "products/product_list.html", context)


@admin_required
def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("seller", "category"), pk=product_id)
    return render(request, "products/product_detail.html", {"product": product})


@admin_required
def product_create(request):
    categories = Category.objects.filter(is_active=True).order_by("name")
    sellers = CustomUser.objects.filter(role="seller", is_active=True).order_by("username")
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            product = form.save()
            for idx, image_file in enumerate(request.FILES.getlist("images")):
                ProductImage.objects.create(product=product, image=image_file, is_main=(idx == 0))
            messages.success(request, "Mahsulot qo'shildi.")
            return redirect("product_list")
        messages.error(request, "Formani tekshiring, ayrim maydonlarda xatolik bor.")
    return render(
        request,
        "products/product_form.html",
        {
            "title": "Mahsulot qo'shish",
            "product": None,
            "categories": categories,
            "sellers": sellers,
            "form": form,
        },
    )


@admin_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    categories = Category.objects.filter(is_active=True).order_by("name")
    sellers = CustomUser.objects.filter(role="seller", is_active=True).order_by("username")
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Mahsulot yangilandi.")
            return redirect("product_detail", product_id=product.id)
        messages.error(request, "Formani tekshiring, ayrim maydonlarda xatolik bor.")
    return render(
        request,
        "products/product_form.html",
        {
            "title": "Mahsulotni tahrirlash",
            "product": product,
            "categories": categories,
            "sellers": sellers,
            "form": form,
        },
    )


@admin_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method in ["POST", "DELETE"]:
        product.delete()
        return JsonResponse({"success": True, "message": "Mahsulot o'chirildi"})
    return JsonResponse({"success": False, "message": "Noto'g'ri so'rov"}, status=405)


@admin_required
@require_POST
def product_approve(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    new_status = request.POST.get("status", "active")
    if new_status not in ["active", "rejected"]:
        return JsonResponse({"success": False, "message": "Noto'g'ri status"}, status=400)
    product.status = new_status
    product.save(update_fields=["status"])
    return JsonResponse({"success": True, "status": product.status})


@admin_required
def category_list(request):
    categories = Category.objects.select_related("parent").order_by("name")
    paginator = Paginator(categories, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "products/category_list.html", {"page_obj": page_obj})


@admin_required
def category_create(request):
    form = CategoryForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kategoriya yaratildi.")
        return redirect("category_list")
    return render(request, "products/category_form.html", {"form": form, "title": _("Kategoriya qo'shish")})


@admin_required
def category_edit(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kategoriya yangilandi.")
        return redirect("category_list")
    return render(request, "products/category_form.html", {"form": form, "title": _("Kategoriya tahrirlash")})


@admin_required
def category_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == "POST":
        category.delete()
        return JsonResponse({"success": True, "message": "Kategoriya o'chirildi"})
    return JsonResponse({"success": False, "message": "Noto'g'ri so'rov"}, status=405)


@admin_required
def product_export(request):
    file_format = request.GET.get("format", "xlsx")
    resource = ProductResource()
    dataset = resource.export()

    if file_format == "csv":
        response = HttpResponse(dataset.csv, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="mahsulotlar.csv"'
    else:
        response = HttpResponse(
            dataset.xlsx,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="mahsulotlar.xlsx"'
    return response


@admin_required
def product_import(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        resource = ProductResource()

        if file.name.endswith(".csv"):
            dataset = CSV().create_dataset(file.read().decode("utf-8"))
        elif file.name.endswith((".xlsx", ".xls")):
            dataset = XLSX().create_dataset(file.read())
        else:
            messages.error(request, "Faqat CSV yoki Excel fayl yuklang")
            return redirect("product_list")

        result = resource.import_data(dataset, dry_run=True)
        if result.has_errors():
            for row in result.row_errors():
                for error in row[1]:
                    messages.error(request, f"Qator {row[0]}: {error.error}")
            return redirect("product_list")

        resource.import_data(dataset, dry_run=False)
        messages.success(request, f"{result.total_rows} ta mahsulot import qilindi")
        return redirect("product_list")

    return render(request, "products/product_import.html")


@admin_required
def category_export(request):
    resource = CategoryResource()
    dataset = resource.export()
    response = HttpResponse(
        dataset.xlsx,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="kategoriyalar.xlsx"'
    return response


@admin_required
def product_image_upload(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST" and request.FILES.getlist("images"):
        files = request.FILES.getlist("images")
        for idx, image_file in enumerate(files):
            is_main = idx == 0 and not product.images.filter(is_main=True).exists()
            ProductImage.objects.create(product=product, image=image_file, is_main=is_main)
        messages.success(request, f"{len(files)} ta rasm yuklandi")
    return redirect("product_detail", product_id=product_id)


@admin_required
@require_POST
def product_image_delete(request, product_id, image_id):
    image = get_object_or_404(ProductImage, pk=image_id, product_id=product_id)
    image.delete()
    return JsonResponse({"success": True})


@admin_required
@require_POST
def product_image_set_main(request, product_id, image_id):
    product = get_object_or_404(Product, pk=product_id)
    product.images.update(is_main=False)
    product.images.filter(pk=image_id).update(is_main=True)
    return JsonResponse({"success": True})
