from django.urls import path
from .views import catalog, conditioner_detail, add_review, compare_conditioners


urlpatterns = [
    path('', catalog, name='catalog'),
    path('compare/', compare_conditioners, name='compare_conditioners'),
    path('<int:conditioner_id>/', conditioner_detail, name='conditioner_detail'),
    path('<int:conditioner_id>/review/', add_review, name='add_review'),
    ]
