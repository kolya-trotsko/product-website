import json
import os
import subprocess
from unittest.mock import patch
from urllib.error import URLError

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from catalog.models import CatalogProduct, CatalogProductPrice, Company, Review
from ks_klimat_kh.models import NotificationOutbox, TelegramUpdate
from ks_klimat_kh.seo import product_schema
from ks_klimat_kh.views import server_error


def create_product(name="Hardening AC", **overrides):
    company = Company.objects.create(name=f"{name} Brand")
    defaults = {
        "brand": company,
        "name": name,
        "model": name,
        "slug": name.lower().replace(" ", "-"),
        "source_key": f"test-{name.lower().replace(' ', '-')}",
        "category": "air_conditioners",
        "product_type": CatalogProduct.TYPE_AIR_CONDITIONER,
        "description": "Test",
        "is_active": True,
        "is_indexable": True,
    }
    defaults.update(overrides)
    return CatalogProduct.objects.create(**defaults)


class ProductionSettingsTests(TestCase):
    def test_missing_production_secret_fails_startup(self):
        env = os.environ.copy()
        env.update(
            {
                "DEBUG": "False",
                "DJANGO_ENV": "production",
                "ALLOWED_HOSTS": "example.com",
                "SITE_URL": "https://example.com",
                "REDIS_URL": "redis://localhost:6379/0",
            }
        )
        env.pop("SECRET_KEY", None)
        result = subprocess.run(
            [os.path.join(os.getcwd(), "venv", "Scripts", "python.exe"), "manage.py", "check"],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY", result.stderr + result.stdout)


class ReviewEndpointHardeningTests(TestCase):
    def setUp(self):
        self.product = create_product()
        self.user = get_user_model().objects.create_user(
            username="review-hardening",
            email="review-hardening@example.com",
            password="pass1234",
        )

    def test_review_get_returns_405(self):
        response = self.client.get(reverse("add_review", args=[self.product.id]))
        self.assertEqual(response.status_code, 405)

    def test_anonymous_review_does_not_create_row(self):
        response = self.client.post(reverse("add_review", args=[self.product.id]), {"text": "x", "rating": 5})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_duplicate_review_is_rejected(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add_review", args=[self.product.id]), {"text": "first", "rating": 5})
        self.client.post(reverse("add_review", args=[self.product.id]), {"text": "second", "rating": 4})
        self.assertEqual(Review.objects.count(), 1)

    def test_rating_outside_range_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(conditioner=self.product, user=self.user, text="bad", rating=6)


class OrderAndRateLimitHardeningTests(TestCase):
    def test_product_without_colors_can_be_ordered(self):
        product = create_product("No Color AC")
        response = self.client.post(
            reverse("conditioner_detail", args=[product.id]),
            {
                "name": "Ivan",
                "phone": "+380501112233",
                "address": "Test street 1",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NotificationOutbox.objects.filter(event_type="conditioner_order_created").count(), 1)

    @override_settings(RATE_LIMITS={"home_order": {"limit": 1, "window": 60}})
    def test_rate_limit_returns_retry_after(self):
        payload = {"name": "Ivan", "phone": "+380501112233", "option": "Office"}
        self.client.post(reverse("home"), payload)
        response = self.client.post(reverse("home"), payload)
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response)


class NotificationOutboxHardeningTests(TestCase):
    @override_settings(
        TELEGRAM_NOTIFICATIONS_ENABLED=True,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_ADMIN_CHAT_IDS=["12345"],
    )
    @patch("ks_klimat_kh.telegram_notify.request.urlopen", side_effect=URLError("timeout"))
    def test_failed_notification_can_retry(self, mock_urlopen):
        NotificationOutbox.objects.create(
            event_type="test",
            deduplication_key="test:1",
            payload={"text": "hello"},
        )

        from django.core.management import call_command

        call_command("process_notification_outbox")

        notification = NotificationOutbox.objects.get()
        self.assertEqual(notification.status, NotificationOutbox.STATUS_PENDING)
        self.assertEqual(notification.attempt_count, 1)
        self.assertIsNone(notification.sent_at)
        mock_urlopen.assert_called()


@override_settings(
    TELEGRAM_NOTIFICATIONS_ENABLED=True,
    TELEGRAM_BOT_TOKEN="token",
    TELEGRAM_ADMIN_CHAT_IDS=["1001"],
    TELEGRAM_WEBHOOK_SECRET="secret123",
)
class TelegramWebhookHardeningTests(TestCase):
    def test_wrong_secret_is_rejected(self):
        response = self.client.post(
            reverse("telegram_webhook", kwargs={"secret": "wrong"}),
            data={"update_id": 1},
            content_type="application/json",
            HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="wrong",
        )
        self.assertEqual(response.status_code, 403)

    @patch("ks_klimat_kh.telegram_bot.send_message")
    def test_duplicate_update_is_ignored(self, mock_send):
        payload = {
            "update_id": 42,
            "message": {
                "chat": {"id": 555},
                "from": {"id": 555, "username": "lead_user", "first_name": "Lead"},
                "text": "/new",
            },
        }
        url = reverse("telegram_webhook", kwargs={"secret": "secret123"})
        self.client.post(url, data=payload, content_type="application/json")
        self.client.post(url, data=payload, content_type="application/json")
        self.assertEqual(TelegramUpdate.objects.filter(update_id=42).count(), 1)
        self.assertEqual(mock_send.call_count, 1)


class SeoHardeningTests(TestCase):
    def test_json_ld_omits_offer_without_price(self):
        product = create_product("No Price AC")
        request = RequestFactory().get(reverse("conditioner_detail", args=[product.id]))
        request.get_host = lambda: "testserver"
        data = json.loads(product_schema(request, product, Review.objects.none()))
        self.assertNotIn("offers", data)

    def test_json_ld_includes_offer_with_price(self):
        product = create_product("Priced AC")
        CatalogProductPrice.objects.create(
            product=product,
            price_type=CatalogProductPrice.TYPE_RETAIL,
            currency=CatalogProductPrice.CURRENCY_UAH,
            amount="1000.00",
            source_sheet="test",
            source_row=1,
        )
        request = RequestFactory().get(reverse("conditioner_detail", args=[product.id]))
        request.get_host = lambda: "testserver"
        data = json.loads(product_schema(request, product, Review.objects.none()))
        self.assertEqual(data["offers"]["price"], "1000.00")


class ErrorAndHealthTests(TestCase):
    def test_healthz_reports_web_process(self):
        response = self.client.get(reverse("healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["checks"]["web"], "ok")

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"], WHITENOISE_MANIFEST_STRICT=False)
    def test_custom_404_renders_with_debug_false(self):
        response = self.client.get("/missing-page/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Сторінку не знайдено", status_code=404)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"], WHITENOISE_MANIFEST_STRICT=False)
    def test_custom_500_handler_renders(self):
        response = server_error(RequestFactory().get("/boom/"))
        self.assertEqual(response.status_code, 500)
        self.assertIn("Помилка сервера", response.content.decode("utf-8"))
