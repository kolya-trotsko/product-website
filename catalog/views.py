from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from urllib.parse import urlencode
from django.db.models import Q
from company_info.models import CompanyInfo
from .models import CatalogProduct, Review, Company, Color
from .forms import ReviewForm, ConditionerOrderForm
from ks_klimat_kh.rate_limit import get_client_ip, is_rate_limited
from ks_klimat_kh.seo import local_business_schema, product_schema
from ks_klimat_kh.telegram_notify import notify_conditioner_order

ORDER_ACCEPTED_MESSAGE = "Дякуємо за звернення. Наш менеджер зв’яжеться з вами найближчим часом."

PUBLIC_CATALOG_PRODUCT_TYPES = (
    CatalogProduct.TYPE_AIR_CONDITIONER,
    CatalogProduct.TYPE_AIR_CONDITIONER_SET,
    CatalogProduct.TYPE_MULTI_SPLIT,
    CatalogProduct.TYPE_SEMI_INDUSTRIAL,
    CatalogProduct.TYPE_HEAT_PUMP,
)


def catalog(request):
    contacts = CompanyInfo.objects.first()
    search_query = request.GET.get('query', '')
    color_filter = request.GET.get('color', '')
    company_filter = request.GET.get('company', '')
    type_filter = request.GET.get('type', '')
    stock_filter = request.GET.get('stock', '')
    warranty_min = request.GET.get('warranty_min', '')
    area_min = request.GET.get('area_min', '')
    area_max = request.GET.get('area_max', '')
    page_number = request.GET.get('page', 1)

    conditioners = (
        CatalogProduct.objects
        .select_related("brand")
        .prefetch_related("colors", "prices", "images")
        .filter(is_active=True, is_indexable=True, product_type__in=PUBLIC_CATALOG_PRODUCT_TYPES)
        .order_by('name')
    )

    if search_query:
        conditioners = conditioners.filter(
            Q(name__icontains=search_query)
            | Q(model__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    if color_filter:
        conditioners = conditioners.filter(colors__name=color_filter)

    if company_filter:
        conditioners = conditioners.filter(brand__name=company_filter)

    if type_filter:
        conditioners = conditioners.filter(product_type=type_filter)

    if stock_filter == "in_stock":
        conditioners = conditioners.filter(is_in_stock=True)
    elif stock_filter == "out_of_stock":
        conditioners = conditioners.filter(is_in_stock=False)

    if warranty_min.isdigit():
        conditioners = conditioners.filter(warranty_months__gte=int(warranty_min))

    if area_min.isdigit():
        conditioners = conditioners.filter(recommended_area_m2__gte=int(area_min))
    if area_max.isdigit():
        conditioners = conditioners.filter(recommended_area_m2__lte=int(area_max))

    conditioners = conditioners.distinct()

    paginator = Paginator(conditioners, 15)
    conditioners = paginator.get_page(page_number)

    colors = (
        Color.objects
        .filter(
            catalog_products__is_active=True,
            catalog_products__is_indexable=True,
            catalog_products__product_type__in=PUBLIC_CATALOG_PRODUCT_TYPES,
        )
        .values_list("name", flat=True)
        .distinct()
        .order_by("name")
    )
    companies = (
        Company.objects
        .filter(
            catalog_products__is_active=True,
            catalog_products__is_indexable=True,
            catalog_products__product_type__in=PUBLIC_CATALOG_PRODUCT_TYPES,
        )
        .values_list("name", flat=True)
        .distinct()
        .order_by("name")
    )

    return render(request, 'catalog/catalog.html', {
        'seo_title': 'Каталог кондиціонерів у Харкові | KS KLIMAT KH',
        'seo_description': (
            'Каталог кондиціонерів у Харкові: інверторні та звичайні моделі, фільтр за брендом, '
            'типом, площею приміщення, гарантією та наявністю.'
        ),
        'seo_noindex': bool(request.GET),
        'conditioners': conditioners,
        'search_query': search_query,
        'color_filter': color_filter,
        'company_filter': company_filter,
        'type_filter': type_filter,
        'stock_filter': stock_filter,
        'warranty_min': warranty_min,
        'area_min': area_min,
        'area_max': area_max,
        'contacts': contacts,
        'colors': colors,
        'companies': companies,
        'type_choices': [
            choice for choice in CatalogProduct.TYPE_CHOICES if choice[0] in PUBLIC_CATALOG_PRODUCT_TYPES
        ],
        'structured_data': local_business_schema(request, contacts),
    })


def conditioner_detail(request, conditioner_id):
    conditioner = get_object_or_404(
        CatalogProduct.objects.select_related("brand").prefetch_related("colors", "prices", "images"),
        id=conditioner_id,
        is_active=True,
        is_indexable=True,
    )
    contacts = CompanyInfo.objects.first()
    reviews = Review.objects.select_related("user").filter(conditioner=conditioner)
    order_form = ConditionerOrderForm(conditioner=conditioner)
    gallery_images = []
    if conditioner.main_image:
        gallery_images.append(conditioner.main_image)
    for product_image in conditioner.images.all():
        if product_image.image and product_image.image.name not in {image.name for image in gallery_images}:
            gallery_images.append(product_image.image)
    seo_image = request.build_absolute_uri(gallery_images[0].url) if gallery_images else ""

    if request.method == 'POST':
        if is_rate_limited(request, "conditioner_order"):
            return HttpResponse(status=429)
        order_form = ConditionerOrderForm(request.POST, conditioner=conditioner)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.conditioner = conditioner
            order.source_page = request.path
            order.client_ip = get_client_ip(request)
            order.save()
            notify_conditioner_order(order, request.path)
            messages.success(request, ORDER_ACCEPTED_MESSAGE, extra_tags="toast-order-accepted")
            return redirect('conditioner_detail', conditioner_id=conditioner_id)

    return render(request, 'catalog/conditioner_detail.html', {
        'seo_title': f'{conditioner.name} купити в Харкові | KS KLIMAT KH',
        'seo_description': (
            f'{conditioner.name}: ціна {conditioner.primary_price or "-"} {conditioner.primary_currency or ""}, виробник {conditioner.brand.name}, '
            f'площа до {conditioner.recommended_area_m2} м², гарантія {conditioner.warranty_months} міс.'
        ),
        'seo_image': seo_image,
        'structured_data': product_schema(request, conditioner, reviews),
        'conditioner': conditioner,
        'gallery_images': gallery_images,
        'contacts': contacts,
        'reviews': reviews,
        'order_form': order_form,
    })


def add_review(request, conditioner_id):
    conditioner = get_object_or_404(CatalogProduct, id=conditioner_id, is_active=True, is_indexable=True)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, 'Спочатку увійдіть у профіль, щоб залишити відгук.')
            login_url = reverse('account_login')
            return redirect(f"{login_url}?next={request.path}")
        if is_rate_limited(request, "review"):
            return HttpResponse(status=429)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.conditioner = conditioner
            review.user = request.user
            review.save()
            messages.success(request, 'Відгук додано.')
        else:
            for field, errors in form.errors.items():
                field_label = form.fields.get(field).label if field in form.fields else field
                for error in errors:
                    messages.error(request, f"{field_label}: {error}")

    return redirect('conditioner_detail', conditioner_id=conditioner_id)


def compare_conditioners(request):
    contacts = CompanyInfo.objects.first()
    ids = request.GET.getlist("ids")
    parsed_ids = [int(i) for i in ids if i.isdigit()]
    conditioners = list(
        CatalogProduct.objects.select_related("brand")
        .prefetch_related("colors", "prices", "images")
        .filter(id__in=parsed_ids, is_active=True, is_indexable=True)[:4]
    )

    for conditioner in conditioners:
        remaining_ids = [item_id for item_id in parsed_ids if item_id != conditioner.id]
        if remaining_ids:
            conditioner.compare_remove_url = f"{reverse('compare_conditioners')}?{urlencode({'ids': remaining_ids}, doseq=True)}"
        else:
            conditioner.compare_remove_url = reverse("catalog")

    return render(
        request,
        "catalog/compare.html",
        {
            "title": "Compare",
            "seo_title": "Порівняння кондиціонерів | KS KLIMAT KH",
            "seo_description": "Порівняння обраних моделей кондиціонерів за ціною, типом, площею, гарантією та наявністю.",
            "seo_noindex": True,
            "contacts": contacts,
            "conditioners": conditioners,
        },
    )
