from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from service.models import BotLead, Order


@override_settings(
    TELEGRAM_NOTIFICATIONS_ENABLED=True,
    TELEGRAM_BOT_TOKEN="token",
    TELEGRAM_ADMIN_CHAT_IDS=["1001"],
    TELEGRAM_WEBHOOK_SECRET="secret123",
)
class TelegramBotWebhookTests(TestCase):
    def _post(self, payload):
        return self.client.post(
            reverse("telegram_webhook", kwargs={"secret": "secret123"}),
            data=payload,
            content_type="application/json",
        )

    @patch("ks_klimat_kh.telegram_bot.send_message")
    def test_lead_intent_creates_bot_lead(self, mock_send):
        payload = {
            "message": {
                "chat": {"id": 777},
                "from": {"id": 777, "username": "lead_user", "first_name": "Lead"},
                "text": "хочу консультацію",
            }
        }
        response = self._post(payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BotLead.objects.count(), 1)
        self.assertEqual(BotLead.objects.first().intent, BotLead.INTENT_CONSULT)
        mock_send.assert_called()

    @patch("ks_klimat_kh.telegram_bot.send_message")
    def test_assign_command_from_admin_assigns_manager(self, mock_send):
        manager = get_user_model().objects.create_user(
            username="manager1",
            email="m1@example.com",
            password="pass1234",
        )
        order = Order.objects.create(name="Client", phone="+380500000001", place="Office")

        payload = {
            "message": {
                "chat": {"id": 1001},
                "from": {"id": 1001, "username": "admin"},
                "text": f"/assign home {order.id} @manager1",
            }
        }
        response = self._post(payload)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.manager_id, manager.id)
        self.assertEqual(order.status, "in_progress")
        mock_send.assert_called()

    @patch("ks_klimat_kh.telegram_bot.send_message")
    def test_non_admin_cannot_use_commands(self, mock_send):
        payload = {
            "message": {
                "chat": {"id": 555},
                "from": {"id": 555, "username": "non_admin"},
                "text": "/new",
            }
        }
        response = self._post(payload)
        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_with("Команди доступні лише адміну.", chat_id=555)
