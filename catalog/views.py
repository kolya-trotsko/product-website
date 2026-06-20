from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
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

    conditioners = AirConditioner.objects.filter(name__icontains=search_query).order_by('name')

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
    conditioner = get_object_or_404(AirConditioner, id=conditioner_id)
    contacts = CompanyInfo.objects.first()
    reviews = Review.objects.filter(conditioner_id=conditioner_id)

    if request.method == 'POST':
        if is_rate_limited(request, "conditioner_order"):
            return HttpResponse(status=429)
        form = ConditionerOrderForm(request.POST, conditioner=conditioner)
        if form.is_valid():
            order = form.save(commit=False)
            order.conditioner = conditioner
            order.save()
            return redirect('conditioner_detail', conditioner_id=conditioner_id)

    return render(request, 'catalog/conditioner_detail.html', {
        'conditioner': conditioner,
        'contacts': contacts,
        'reviews': reviews,
    })


def add_review(request, conditioner_id):
    conditioner = get_object_or_404(AirConditioner, id=conditioner_id)

    if request.method == 'POST':
        if is_rate_limited(request, "review"):
            return HttpResponse(status=429)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.conditioner = conditioner
            review.save()
            messages.success(request, 'Review submitted.')

    return redirect('conditioner_detail', conditioner_id=conditioner_id)
