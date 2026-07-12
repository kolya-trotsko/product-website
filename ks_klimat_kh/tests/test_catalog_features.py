import sys
from unittest import skipIf

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import CatalogProduct, CatalogProductPrice, Color, Company, Review


def add_price(product, amount):
    CatalogProductPrice.objects.create(
        product=product,
        price_type=CatalogProductPrice.TYPE_RETAIL,
        currency=CatalogProductPrice.CURRENCY_UAH,
        amount=amount,
        source_sheet="test",
        source_row=product.id,
    )


@skipIf(
    sys.version_info >= (3, 14),
    "Django 4.2 test client context-copy is incompatible with Python 3.14 in this environment.",
)
class CatalogFeatureTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="TestCo")
        self.color = Color.objects.create(name="White", hash="#ffffff")
        self.ac_in = CatalogProduct.objects.create(
            brand=self.company,
            name="AC Inverter",
            model="AC Inverter",
            slug="ac-inverter",
            source_key="test-ac-inverter",
            category="air_conditioners",
            product_type=CatalogProduct.TYPE_AIR_CONDITIONER,
            main_image="catalog/air_conditioner_photos/ac1.png",
            description="desc",
            recommended_area_m2=35,
            is_in_stock=True,
            warranty_months=24,
            specs={"legacy_conditioner_type": "Інверторний"},
        )
        add_price(self.ac_in, "1000.00")
        self.ac_in.colors.add(self.color)
        self.ac_out = CatalogProduct.objects.create(
            brand=self.company,
            name="AC Normal",
            model="AC Normal",
            slug="ac-normal",
            source_key="test-ac-normal",
            category="air_conditioners",
            product_type=CatalogProduct.TYPE_AIR_CONDITIONER,
            main_image="catalog/air_conditioner_photos/ac2.png",
            description="desc",
            recommended_area_m2=20,
            is_in_stock=False,
            warranty_months=12,
            specs={"legacy_conditioner_type": "Звичайний"},
        )
        add_price(self.ac_out, "900.00")
        self.user = get_user_model().objects.create_user(
            username="rating-user",
            email="rating-user@example.com",
            password="pass1234",
        )
        self.user2 = get_user_model().objects.create_user(
            username="rating-user-2",
            email="rating-user-2@example.com",
            password="pass1234",
        )
        self.user3 = get_user_model().objects.create_user(
            username="rating-user-3",
            email="rating-user-3@example.com",
            password="pass1234",
        )

    def test_catalog_filter_by_type_and_stock(self):
        response = self.client.get(
            reverse("catalog"),
            {"type": CatalogProduct.TYPE_AIR_CONDITIONER, "stock": "in_stock"},
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

    def test_catalog_filter_by_rating(self):
        Review.objects.create(conditioner=self.ac_in, user=self.user, text="Great", rating=5)
        Review.objects.create(conditioner=self.ac_in, user=self.user2, text="Good", rating=4)
        Review.objects.create(conditioner=self.ac_out, user=self.user3, text="Average", rating=3)

        response = self.client.get(reverse("catalog"), {"rating": "4.5"})

        self.assertEqual(response.status_code, 200)
        page = response.context["conditioners"]
        ids = [obj.id for obj in page.object_list]
        self.assertIn(self.ac_in.id, ids)
        self.assertNotIn(self.ac_out.id, ids)


class ProductRatingCacheTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="RatingCo")
        self.product = CatalogProduct.objects.create(
            brand=self.company,
            name="Rated AC",
            model="Rated AC",
            slug="rated-ac",
            source_key="test-rated-ac",
            category="air_conditioners",
            product_type=CatalogProduct.TYPE_AIR_CONDITIONER,
            description="desc",
        )
        self.user = get_user_model().objects.create_user(
            username="rating-cache-user",
            email="rating-cache-user@example.com",
            password="pass1234",
        )
        self.user2 = get_user_model().objects.create_user(
            username="rating-cache-user-2",
            email="rating-cache-user-2@example.com",
            password="pass1234",
        )

    def test_rating_cache_updates_after_review_save_and_delete(self):
        review = Review.objects.create(conditioner=self.product, user=self.user, text="Great", rating=5)
        Review.objects.create(conditioner=self.product, user=self.user2, text="Good", rating=4)

        self.product.refresh_from_db()
        self.assertEqual(self.product.rating_count, 2)
        self.assertEqual(str(self.product.rating_avg), "4.50")

        review.delete()
        self.product.refresh_from_db()
        self.assertEqual(self.product.rating_count, 1)
        self.assertEqual(str(self.product.rating_avg), "4.00")
