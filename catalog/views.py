from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from company_info.models import CompanyInfo
from .models import AirConditioner, Review, ConditionerOrder, Color
from .forms import ReviewForm
from django.contrib import messages


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
    conditioner = AirConditioner.objects.get(id=conditioner_id)
    contacts = CompanyInfo.objects.first()
    reviews = Review.objects.filter(conditioner_id=conditioner_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        color_id = request.POST.get('color')

        color = Color.objects.get(id=color_id)

        ConditionerOrder.objects.create(
            name=name, 
            phone=phone, 
            address=address,
            conditioner=conditioner,
            color=color
            )
    
    return render(request, 'catalog/conditioner_detail.html', {
        'conditioner': conditioner, 
        'contacts': contacts,
        'reviews': reviews,
        })


def add_review(request, conditioner_id):
    conditioner = AirConditioner.objects.get(id=conditioner_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.conditioner = conditioner
            user = request.POST.get('user')
            review.user = user
            review.save()
            messages.success(request, 'Ваш відгук було успішно додано!')
            
    return redirect('conditioner_detail', conditioner_id=conditioner_id)