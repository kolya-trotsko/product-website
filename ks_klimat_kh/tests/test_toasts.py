from __future__ import annotations

from unittest.mock import patch

from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from catalog.models import AirConditioner, Color, Company


ORDER_ACCEPTED_TITLE = "Заявку прийнято!"
ORDER_ACCEPTED_TEXT = "Дякуємо за звернення. Наш менеджер зв’яжеться з вами найближчим часом."


class FakeMessage:
    level_tag = "success"
    tags = "success toast-order-accepted"

    def __str__(self):
        return ORDER_ACCEPTED_TEXT


class ToastMessageTemplateTests(SimpleTestCase):
    def test_django_messages_render_as_toasts_not_list_items(self):
        html = render_to_string(
            "base.html",
            {
                "messages": [FakeMessage()],
                "site_name": "KS KLIMAT KH",
                "default_seo_description": "Test description",
                "default_seo_image": "http://testserver/media/logo.png",
                "canonical_url": "http://testserver/",
                "MEDIA_URL": "/media/",
            },
        )

        self.assertIn('class="toast-region"', html)
        self.assertIn("site-toast-success", html)
        self.assertIn(ORDER_ACCEPTED_TITLE, html)
        self.assertIn(ORDER_ACCEPTED_TEXT, html)
        self.assertNotIn('class="messages"', html)
        self.assertNotIn('class="message success"', html)


class ToastMessageIntegrationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="C&H")
        self.color = Color.objects.create(name="Чорний", hash="#111111")
        self.conditioner = AirConditioner.objects.create(
            name="CH-S09FTXAL2-FB",
            price="33199.00",
            photo="imported_products/ch/ch/ch-s09ftxal2-fb_80_35.png",
            description="Test product",
            company=self.company,
        )
        self.conditioner.colors.add(self.color)

    @patch("catalog.views.notify_conditioner_order")
    def test_order_success_message_is_rendered_as_toast_after_redirect(self, _notify):
        response = self.client.post(
            reverse("conditioner_detail", args=[self.conditioner.id]),
            {
                "name": "Іван",
                "phone": "+380501112233",
                "address": "Харків, тестова адреса",
                "color": self.color.id,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="toast-region"')
        self.assertContains(response, "site-toast-success")
        self.assertContains(response, ORDER_ACCEPTED_TITLE)
        self.assertContains(response, ORDER_ACCEPTED_TEXT)
        self.assertNotContains(response, 'class="messages"')
        self.assertNotContains(response, 'class="message success"')
