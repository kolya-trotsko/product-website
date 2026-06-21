from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from company_info.models import CompanyInfo
from .models import AirConditioningService
from catalog.models import Company
from .models import Order, ServiceOrder
from .forms import OrderForm, ServiceOrderForm
from ks_klimat_kh.rate_limit import get_client_ip, is_rate_limited
from ks_klimat_kh.seo import local_business_schema
from ks_klimat_kh.telegram_notify import notify_home_order, notify_service_order

ORDER_ACCEPTED_MESSAGE = "Дякуємо за звернення. Наш менеджер зв’яжеться з вами найближчим часом."


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
                client_ip=get_client_ip(request),
            )
            notify_service_order(order, request.path)
            messages.success(request, ORDER_ACCEPTED_MESSAGE, extra_tags="toast-order-accepted")
            return redirect('service')
        
    return render(request, 'service/service.html', {
                            'seo_title': 'Ремонт і сервіс кондиціонерів у Харкові | KS KLIMAT KH',
                            'seo_description': (
                                'Ремонт, діагностика, чистка та сервісне обслуговування кондиціонерів у Харкові. '
                                'Актуальні ціни на послуги та швидке оформлення заявки.'
                            ),
                            'contacts': contacts, 
                            'services': services,
                            'form': form,
                            'structured_data': local_business_schema(request, contacts),
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
                client_ip=get_client_ip(request),
            )
            notify_home_order(order, request.path)
            messages.success(request, ORDER_ACCEPTED_MESSAGE, extra_tags="toast-order-accepted")
            return redirect('home')
    
    return render(request, 'home/home.html', {
                        'seo_title': 'Чистка кондиціонерів у Харкові | KS KLIMAT KH',
                        'seo_description': (
                            'Комплексна чистка кондиціонерів у Харкові: розбір внутрішнього блоку, мийка фільтрів, '
                            'теплообмінника, вентилятора, дренажу та зовнішнього блоку.'
                        ),
                        'contacts': contacts, 
                        'companies': companies,
                        'form': form,
                        'structured_data': local_business_schema(request, contacts),
                        })


def policy(request):
    contacts = CompanyInfo.objects.first()
    
    return render(request, 'policy/policy.html', {
                        'seo_title': 'Політика конфіденційності | KS KLIMAT KH',
                        'seo_description': 'Політика конфіденційності сайту KS KLIMAT KH: як ми збираємо, використовуємо та захищаємо персональні дані.',
                        'seo_noindex': True,
                        'contacts': contacts, 
                        })
