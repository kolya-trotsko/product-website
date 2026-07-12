import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings

from ks_klimat_kh.models import NotificationOutbox
from ks_klimat_kh.telegram_notify import notify_home_order, send_message


class TelegramNotifyTests(TestCase):
    @override_settings(
        TELEGRAM_NOTIFICATIONS_ENABLED=True,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_ADMIN_CHAT_IDS=["12345"],
    )
    @patch("ks_klimat_kh.telegram_notify.request.urlopen")
    def test_notify_home_order_escapes_html(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b"{}"
        order = SimpleNamespace(
            id=7,
            name='Ivan <script>alert("x")</script>',
            phone="+380500000000",
            place="Office & Home",
            source_page="/service/home/",
        )

        notification = notify_home_order(order, "/service/home/")

        mock_urlopen.assert_not_called()
        self.assertEqual(NotificationOutbox.objects.count(), 1)
        self.assertIn("&lt;script&gt;", notification.payload["text"])
        self.assertIn("Office &amp; Home", notification.payload["text"])

    @override_settings(
        TELEGRAM_NOTIFICATIONS_ENABLED=True,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_ADMIN_CHAT_IDS=["12345"],
    )
    @patch("ks_klimat_kh.telegram_notify.request.urlopen")
    def test_send_message_posts_to_telegram(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b"{}"

        send_message("Hello")

        self.assertTrue(mock_urlopen.called)
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["text"], "Hello")

    @override_settings(
        TELEGRAM_NOTIFICATIONS_ENABLED=False,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_ADMIN_CHAT_IDS=["12345"],
    )
    @patch("ks_klimat_kh.telegram_notify.request.urlopen")
    def test_notify_home_order_skips_when_disabled(self, mock_urlopen):
        order = SimpleNamespace(
            id=1,
            name="User",
            phone="+380500000000",
            place="Office",
            source_page="/service/home/",
        )

        notify_home_order(order, "/service/home/")
        mock_urlopen.assert_not_called()
        self.assertEqual(NotificationOutbox.objects.count(), 1)
