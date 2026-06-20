from django.shortcuts import render, redirect
from django.http import HttpResponse
from company_info.models import CompanyInfo
from .models import AirConditioningService
from catalog.models import Company
from .models import Order, ServiceOrder
from .forms import OrderForm, ServiceOrderForm
from ks_klimat_kh.rate_limit import is_rate_limited
from ks_klimat_kh.telegram_notify import notify_home_order, notify_service_order


def _request_ip(request):
    return request.META.get("REMOTE_ADDR", "")


def service(request):
    contacts = CompanyInfo.objects.first()
    services = AirConditioningService.objects.all()
    service_choices = [(s.service_name, s.service_name) for s in services]
    form = ServiceOrderForm(service_choices=service_choices)

    if request.method == 'POST':
        if is_rate_limited(request, "service_order"):
            return HttpResponse(status=429)
        form = ServiceOrderForm(request.POST, service_choices=service_choices)
        if form.is_valid():
            order = ServiceOrder.objects.create(
                name=form.cleaned_data["name"],
                phone=form.cleaned_data["phone"],
                place=", ".join(form.cleaned_data["services"]),
                address=form.cleaned_data["address"],
                source_page=request.path,
                client_ip=_request_ip(request),
            )
            notify_service_order(order, request.path)
            return redirect('service')
        
    return render(request, 'service/service.html', {
                            'title': 'service', 
                            'contacts': contacts, 
                            'services': services,
                            'form': form,
                            })


def home(request):
    contacts = CompanyInfo.objects.first()
    companies = Company.objects.all()
    form = OrderForm()

    if request.method == 'POST':
        if is_rate_limited(request, "home_order"):
            return HttpResponse(status=429)
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                name=form.cleaned_data["name"],
                phone=form.cleaned_data["phone"],
                place=form.cleaned_data["option"],
                source_page=request.path,
                client_ip=_request_ip(request),
            )
            notify_home_order(order, request.path)
            return redirect('home')
    
    return render(request, 'home/home.html', {
                        'title': 'Home', 
                        'contacts': contacts, 
                        'companies': companies,
                        'form': form,
                        })


def policy(request):
    contacts = CompanyInfo.objects.first()
    
    return render(request, 'policy/policy.html', {
                        'title': 'Policy', 
                        'contacts': contacts, 
                        })
