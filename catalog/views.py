from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from company_info.models import CompanyInfo
from .models import AirConditioner, Review
from .forms import ReviewForm, ConditionerOrderForm
from ks_klimat_kh.rate_limit import is_rate_limited


def catalog(request):
    contacts = CompanyInfo.objects.first()
    search_query = request.GET.get('query', '')
    color_filter = request.GET.get('color', '')
    company_filter = request.GET.get('company', '')
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

    paginator = Paginator(conditioners, 15)
    conditioners = paginator.get_page(page_number)

    colors = AirConditioner.objects.values_list('colors__name', flat=True).distinct()
    companies = AirConditioner.objects.values_list('company__name', flat=True).distinct()

    return render(request, 'catalog/catalog.html', {
        'title': 'Catalog',
        'conditioners': conditioners,
        'search_query': search_query,
        'contacts': contacts,
        'colors': colors,
        'companies': companies,
    })


def conditioner_detail(request, conditioner_id):
    conditioner = get_object_or_404(
        AirConditioner.objects.select_related("company").prefetch_related("colors"),
        id=conditioner_id,
    )
    contacts = CompanyInfo.objects.first()
    reviews = Review.objects.select_related("user").filter(conditioner_id=conditioner_id)
    order_form = ConditionerOrderForm(conditioner=conditioner)

    if request.method == 'POST':
        if is_rate_limited(request, "conditioner_order"):
            return HttpResponse(status=429)
        order_form = ConditionerOrderForm(request.POST, conditioner=conditioner)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.conditioner = conditioner
            order.save()
            return redirect('conditioner_detail', conditioner_id=conditioner_id)

    return render(request, 'catalog/conditioner_detail.html', {
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
