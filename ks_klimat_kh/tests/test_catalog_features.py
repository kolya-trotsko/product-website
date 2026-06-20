import sys

from django.test import TestCase
from django.urls import reverse
from unittest import skipIf

from catalog.models import AirConditioner, Color, Company


@skipIf(
    sys.version_info >= (3, 14),
    "Django 4.2 test client context-copy is incompatible with Python 3.14 in this environment.",
)
class CatalogFeatureTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="TestCo")
        self.color = Color.objects.create(name="White", hash="#ffffff")
        self.ac_in = AirConditioner.objects.create(
            name="AC Inverter",
            conditioner_type=AirConditioner.TYPE_INVERTER,
            price="1000.00",
            photo="catalog/air_conditioner_photos/ac1.png",
            description="desc",
            recommended_area_m2=35,
            is_in_stock=True,
            warranty_months=24,
            company=self.company,
        )
        self.ac_in.colors.add(self.color)
        self.ac_out = AirConditioner.objects.create(
            name="AC Normal",
            conditioner_type=AirConditioner.TYPE_NORMAL,
            price="900.00",
            photo="catalog/air_conditioner_photos/ac2.png",
            description="desc",
            recommended_area_m2=20,
            is_in_stock=False,
            warranty_months=12,
            company=self.company,
        )

    def test_catalog_filter_by_type_and_stock(self):
        response = self.client.get(
            reverse("catalog"),
            {"type": AirConditioner.TYPE_INVERTER, "stock": "in_stock"},
        )
        self.assertEqual(response.status_code, 200)
        page = response.context["conditioners"]
        ids = [obj.id for obj in page.object_list]
        self.assertIn(self.ac_in.id, ids)
        self.assertNotIn(self.ac_out.id, ids)

    def test_compare_page_displays_selected_models(self):
        response = self.client.get(
            reverse("compare_conditioners"),
            {"ids": [str(self.ac_in.id), str(self.ac_out.id)]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AC Inverter")
        self.assertContains(response, "AC Normal")
