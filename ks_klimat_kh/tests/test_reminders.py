from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from service.models import Order, ORDER_STATUS_DONE, ORDER_STATUS_NEW


class ReminderCommandTests(TestCase):
    @patch("service.management.commands.send_order_reminders.notify_unaccepted_order")
    @patch("service.management.commands.send_order_reminders.notify_service_cycle")
    def test_send_order_reminders_marks_fields(self, mock_service_cycle, mock_unaccepted):
        order_new = Order.objects.create(name="New Client", phone="+380500000001", place="Office", status=ORDER_STATUS_NEW)
        order_done = Order.objects.create(name="Done Client", phone="+380500000002", place="Office", status=ORDER_STATUS_DONE)

        old_time = timezone.now() - timedelta(days=400)
        Order.objects.filter(id=order_new.id).update(created_at=timezone.now() - timedelta(hours=3))
        Order.objects.filter(id=order_done.id).update(created_at=old_time)

        call_command("send_order_reminders", "--hours-unaccepted", "2")

        order_new.refresh_from_db()
        order_done.refresh_from_db()
        self.assertIsNotNone(order_new.unaccepted_reminded_at)
        self.assertIsNotNone(order_done.service_reminder_6m_sent_at)
        self.assertIsNotNone(order_done.service_reminder_12m_sent_at)
        self.assertTrue(mock_unaccepted.called)
        self.assertTrue(mock_service_cycle.called)
