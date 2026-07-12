from django.urls import path

from .views import add_review, catalog, compare_conditioners, conditioner_detail

urlpatterns = [
    path("", catalog, name="catalog"),
    path("compare/", compare_conditioners, name="compare_conditioners"),
    path("<int:conditioner_id>/", conditioner_detail, name="conditioner_detail"),
    path("<int:conditioner_id>/review/", add_review, name="add_review"),
]
