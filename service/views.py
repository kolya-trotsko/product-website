from django.shortcuts import render
from company_info.models import CompanyInfo
from .models import AirConditioningService
from catalog.models import Company
from .models import Order, ServiceOrder


def service(request):
    contacts = CompanyInfo.objects.first()
    services = AirConditioningService.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        option = request.POST.getlist('services')
        address = request.POST.get('address')

        ServiceOrder.objects.create(
            name=name, 
            phone=phone, 
            place=option,
            address=address
            )
        
    return render(request, 'service/service.html', {
                            'title': 'service', 
                            'contacts': contacts, 
                            'services': services,
                            })


def home(request):
    contacts = CompanyInfo.objects.first()
    companies = Company.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        option = request.POST.get('option')

        Order.objects.create(
            name=name, 
            phone=phone, 
            place=option
            )
    
    return render(request, 'home/home.html', {
                        'title': 'Home', 
                        'contacts': contacts, 
                        'companies': companies
                        })


def policy(request):
    contacts = CompanyInfo.objects.first()
    
    return render(request, 'policy/policy.html', {
                        'title': 'Policy', 
                        'contacts': contacts, 
                        })