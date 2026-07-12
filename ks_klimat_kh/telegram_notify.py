import json
import logging
from html import escape
from urllib import error, request

from django.conf import settings
from django.db import IntegrityError

from ks_klimat_kh.models import NotificationOutbox

logger = logging.getLogger(__name__)


class TelegramDeliveryError(Exception):
    pass


def _e(value):
    return escape(str(value), quote=True)


def _is_enabled():
    return bool(
        getattr(settings, "TELEGRAM_NOTIFICATIONS_ENABLED", False) and getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    )


def send_message(text, chat_id=None):
    if not _is_enabled():
        raise TelegramDeliveryError("Telegram notifications are disabled or not configured.")

    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    target_chats = [chat_id] if chat_id is not None else list(getattr(settings, "TELEGRAM_ADMIN_CHAT_IDS", []))
    if not target_chats:
        raise TelegramDeliveryError("Telegram target chat list is empty.")

    for target in target_chats:
        payload = json.dumps(
            {
                "chat_id": target,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
        ).encode("utf-8")
        req = request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=8) as response:  # nosec B310
                response.read()
        except (error.URLError, error.HTTPError, TimeoutError) as exc:
            logger.warning("Failed to send telegram message to chat %s", target, exc_info=True)
            raise TelegramDeliveryError("Telegram API request failed.") from exc
    return {"sent": True, "chat_ids": target_chats}


def enqueue_telegram_notification(event_type, deduplication_key, text, **metadata):
    payload = {"text": text}
    payload.update(metadata)
    try:
        notification, _ = NotificationOutbox.objects.get_or_create(
            deduplication_key=deduplication_key,
            defaults={
                "event_type": event_type,
                "payload": payload,
            },
        )
    except IntegrityError:
        notification = NotificationOutbox.objects.get(deduplication_key=deduplication_key)
    return notification


def notify_home_order(order, request_path=""):
    text = (
        "🆕 <b>Нове замовлення (Головна)</b>\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Ім'я: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>\n"
        f"Тип: {_e(order.place)}\n"
        f"Сторінка: <code>{_e(request_path or order.source_page)}</code>"
    )
    return enqueue_telegram_notification("home_order_created", f"home-order-created:{order.id}", text)


def notify_service_order(order, request_path=""):
    text = (
        "🆕 <b>Нове замовлення (Послуги)</b>\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Ім'я: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>\n"
        f"Адреса: {_e(order.address)}\n"
        f"Послуги: {_e(order.place)}\n"
        f"Сторінка: <code>{_e(request_path or order.source_page)}</code>"
    )
    return enqueue_telegram_notification("service_order_created", f"service-order-created:{order.id}", text)


def notify_conditioner_order(order, request_path=""):
    color_name = order.color.name if order.color else "-"
    text = (
        "🆕 <b>Нове замовлення (Каталог)</b>\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Ім'я: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>\n"
        f"Адреса: {_e(order.address)}\n"
        f"Товар: {_e(order.conditioner.name)}\n"
        f"Колір: {_e(color_name)}\n"
        f"Сторінка: <code>{_e(request_path or order.source_page)}</code>"
    )
    return enqueue_telegram_notification("conditioner_order_created", f"conditioner-order-created:{order.id}", text)


def notify_unaccepted_order(order_type, order):
    text = (
        "⏱ <b>Неприйнята заявка</b>\n"
        f"Тип: {_e(order_type)}\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Клієнт: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>\n"
        f"Створено: {_e(order.created_at)}"
    )
    return enqueue_telegram_notification(
        "unaccepted_order_reminder",
        f"unaccepted:{order_type}:{order.id}",
        text,
        model_label=order._meta.label_lower,
        object_id=order.id,
        reminder_field="unaccepted_reminded_at",
    )


def notify_service_cycle(order_type, order, months):
    text = (
        "🔁 <b>Нагадування про сервіс</b>\n"
        f"Період: {_e(months)} міс.\n"
        f"Тип заявки: {_e(order_type)}\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Клієнт: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>"
    )
    return enqueue_telegram_notification(
        "service_cycle_reminder",
        f"service-cycle:{months}:{order_type}:{order.id}",
        text,
        model_label=order._meta.label_lower,
        object_id=order.id,
        reminder_field=f"service_reminder_{months}m_sent_at",
    )
