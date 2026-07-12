from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from ks_klimat_kh.models import NotificationOutbox
from service.models import ORDER_STATUS_DONE, ORDER_STATUS_NEW, Order


class ReminderCommandTests(TestCase):
    def test_send_order_reminders_enqueues_without_marking_sent_fields(self):
        order_new = Order.objects.create(
            name="New Client", phone="+380500000001", place="Office", status=ORDER_STATUS_NEW
        )
        order_done = Order.objects.create(
            name="Done Client", phone="+380500000002", place="Office", status=ORDER_STATUS_DONE
        )

        old_time = timezone.now() - timedelta(days=400)
        Order.objects.filter(id=order_new.id).update(created_at=timezone.now() - timedelta(hours=3))
        Order.objects.filter(id=order_done.id).update(completed_at=old_time)

        call_command("send_order_reminders", "--hours-unaccepted", "2")

        order_new.refresh_from_db()
        order_done.refresh_from_db()
        self.assertIsNone(order_new.unaccepted_reminded_at)
        self.assertIsNone(order_done.service_reminder_6m_sent_at)
        self.assertIsNone(order_done.service_reminder_12m_sent_at)
        self.assertEqual(NotificationOutbox.objects.count(), 2)
        self.assertTrue(NotificationOutbox.objects.filter(deduplication_key=f"unaccepted:home:{order_new.id}").exists())
        self.assertTrue(
            NotificationOutbox.objects.filter(deduplication_key=f"service-cycle:12:home:{order_done.id}").exists()
        )

        call_command("send_order_reminders", "--hours-unaccepted", "2")
        self.assertEqual(NotificationOutbox.objects.count(), 2)

    @patch("ks_klimat_kh.management.commands.process_notification_outbox.send_message")
    def test_outbox_worker_marks_reminder_after_successful_delivery(self, mock_send):
        order = Order.objects.create(
            name="Done Client", phone="+380500000002", place="Office", status=ORDER_STATUS_DONE
        )
        Order.objects.filter(id=order.id).update(completed_at=timezone.now() - timedelta(days=181))
        call_command("send_order_reminders")

        call_command("process_notification_outbox")

        order.refresh_from_db()
        self.assertIsNotNone(order.service_reminder_6m_sent_at)
        self.assertTrue(NotificationOutbox.objects.filter(status=NotificationOutbox.STATUS_SENT).exists())
        mock_send.assert_called()
