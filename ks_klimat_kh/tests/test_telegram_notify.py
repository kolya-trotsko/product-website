import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from ks_klimat_kh.telegram_notify import notify_home_order


class TelegramNotifyTests(SimpleTestCase):
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

        notify_home_order(order, "/service/home/")

        self.assertTrue(mock_urlopen.called)
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode("utf-8"))
        self.assertIn("&lt;script&gt;", payload["text"])
        self.assertIn("Office &amp; Home", payload["text"])

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
