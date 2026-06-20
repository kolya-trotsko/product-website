from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from company_info.models import CompanyInfo
from .models import AirConditioner, Review, Company, Color
from .forms import ReviewForm, ConditionerOrderForm
from ks_klimat_kh.rate_limit import get_client_ip, is_rate_limited
from ks_klimat_kh.seo import local_business_schema, product_schema
from ks_klimat_kh.telegram_notify import notify_conditioner_order

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
        AirConditioner.objects
        .select_related("company")
        .prefetch_related("colors")
        .filter(name__icontains=search_query)
        .order_by('name')
    )

    if color_filter:
        conditioners = conditioners.filter(colors__name=color_filter)

    if company_filter:
        conditioners = conditioners.filter(company__name=company_filter)

    if type_filter:
        conditioners = conditioners.filter(conditioner_type=type_filter)

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

    paginator = Paginator(conditioners, 15)
    conditioners = paginator.get_page(page_number)

    colors = Color.objects.values_list("name", flat=True).order_by("name")
    companies = Company.objects.values_list("name", flat=True).order_by("name")

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
        'type_choices': AirConditioner.TYPE_CHOICES,
        'structured_data': local_business_schema(request, contacts),
    })


def conditioner_detail(request, conditioner_id):
    conditioner = get_object_or_404(
        AirConditioner.objects.select_related("company").prefetch_related("colors"),
        id=conditioner_id,
    )
    contacts = CompanyInfo.objects.first()
    reviews = Review.objects.select_related("user").filter(conditioner_id=conditioner_id)
    order_form = ConditionerOrderForm(conditioner=conditioner)
    seo_image = request.build_absolute_uri(conditioner.photo.url) if conditioner.photo else ""

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
            messages.success(request, "Дякуємо, заявку на кондиціонер прийнято. Ми зв'яжемося з вами найближчим часом.")
            return redirect('conditioner_detail', conditioner_id=conditioner_id)

    return render(request, 'catalog/conditioner_detail.html', {
        'seo_title': f'{conditioner.name} купити в Харкові | KS KLIMAT KH',
        'seo_description': (
            f'{conditioner.name}: ціна {conditioner.price} грн, виробник {conditioner.company.name}, '
            f'площа до {conditioner.recommended_area_m2} м², гарантія {conditioner.warranty_months} міс.'
        ),
        'seo_image': seo_image,
        'structured_data': product_schema(request, conditioner, reviews),
        'conditioner': conditioner,
        'contacts': contacts,
        'reviews': reviews,
        'order_form': order_form,
    })


def add_review(request, conditioner_id):
    conditioner = get_object_or_404(AirConditioner, id=conditioner_id)

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
    conditioners = (
        AirConditioner.objects.select_related("company")
        .prefetch_related("colors")
        .filter(id__in=parsed_ids)[:4]
    )
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
