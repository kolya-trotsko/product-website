from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.forms import ConditionerOrderForm, ReviewForm
from catalog.models import AirConditioner, Color, Company
from service.forms import OrderForm, ServiceOrderForm


class ReviewFormTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name="Test Company")
        self.conditioner = AirConditioner.objects.create(
            name="Test AC",
            price="1000.00",
            photo="catalog/air_conditioner_photos/test.png",
            description="Test description",
            company=company,
        )
        self.user = get_user_model().objects.create_user(
            username="reviewer",
            email="reviewer@example.com",
            password="pass1234",
        )

    def test_review_form_rejects_short_text(self):
        form = ReviewForm(data={"text": "short", "rating": 5})
        self.assertFalse(form.is_valid())
        self.assertIn("text", form.errors)

    def test_review_form_rejects_invalid_rating(self):
        form = ReviewForm(data={"text": "This is a long enough review text.", "rating": 6})
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_review_form_accepts_valid_payload(self):
        form = ReviewForm(data={"text": "This is a long enough review text.", "rating": 5})
        self.assertTrue(form.is_valid())


class ConditionerOrderFormTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name="Order Company")
        self.conditioner = AirConditioner.objects.create(
            name="Order AC",
            price="1500.00",
            photo="catalog/air_conditioner_photos/test-order.png",
            description="Order test description",
            company=company,
        )
        self.allowed_color = Color.objects.create(name="White", hash="#ffffff")
        self.disallowed_color = Color.objects.create(name="Black", hash="#000000")
        self.conditioner.colors.add(self.allowed_color)

    def test_order_form_rejects_color_not_available_for_conditioner(self):
        form = ConditionerOrderForm(
            data={
                "name": "Ivan",
                "phone": "+380501112233",
                "address": "Test street 1",
                "color": self.disallowed_color.id,
            },
            conditioner=self.conditioner,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("color", form.errors)

    def test_order_form_accepts_available_color(self):
        form = ConditionerOrderForm(
            data={
                "name": "Ivan",
                "phone": "+380501112233",
                "address": "Test street 1",
                "color": self.allowed_color.id,
            },
            conditioner=self.conditioner,
        )
        self.assertTrue(form.is_valid())


class ServiceFormsTests(TestCase):
    def test_order_form_rejects_invalid_phone(self):
        form = OrderForm(data={"name": "User", "phone": "abc", "option": "Office"})
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_service_order_form_requires_service_selection(self):
        form = ServiceOrderForm(
            data={
                "name": "User",
                "phone": "+380501112233",
                "address": "Street 1",
            },
            service_choices=[("Cleaning", "Cleaning")],
        )
        self.assertFalse(form.is_valid())
        self.assertIn("services", form.errors)

    def test_service_order_form_accepts_valid_payload(self):
        form = ServiceOrderForm(
            data={
                "name": "User",
                "phone": "+380501112233",
                "address": "Street 1",
                "services": ["Cleaning"],
            },
            service_choices=[("Cleaning", "Cleaning")],
        )
        self.assertTrue(form.is_valid())
