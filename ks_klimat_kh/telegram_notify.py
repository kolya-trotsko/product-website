import json
import logging
from html import escape
from urllib import error, request

from django.conf import settings


logger = logging.getLogger(__name__)


def _e(value):
    return escape(str(value), quote=True)


def _is_enabled():
    return bool(getattr(settings, "TELEGRAM_NOTIFICATIONS_ENABLED", False) and getattr(settings, "TELEGRAM_BOT_TOKEN", ""))


def send_message(text, chat_id=None):
    if not _is_enabled():
        return

    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    target_chats = [chat_id] if chat_id is not None else list(getattr(settings, "TELEGRAM_ADMIN_CHAT_IDS", []))

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
            with request.urlopen(req, timeout=8) as response:
                response.read()
        except (error.URLError, error.HTTPError, TimeoutError) as exc:
            logger.warning("Failed to send telegram message to %s: %s", target, exc)


def notify_home_order(order, request_path=""):
    text = (
        "🆕 <b>Нове замовлення (Головна)</b>\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Ім'я: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>\n"
        f"Тип: {_e(order.place)}\n"
        f"Сторінка: <code>{_e(request_path or order.source_page)}</code>"
    )
    send_message(text)


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
    send_message(text)


def notify_conditioner_order(order, request_path=""):
    text = (
        "🆕 <b>Нове замовлення (Каталог)</b>\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Ім'я: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>\n"
        f"Адреса: {_e(order.address)}\n"
        f"Товар: {_e(order.conditioner.name)}\n"
        f"Колір: {_e(order.color.name)}\n"
        f"Сторінка: <code>{_e(request_path or order.source_page)}</code>"
    )
    send_message(text)


def notify_unaccepted_order(order_type, order):
    text = (
        "⏱ <b>Неприйнята заявка</b>\n"
        f"Тип: {_e(order_type)}\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Клієнт: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>\n"
        f"Створено: {_e(order.created_at)}"
    )
    send_message(text)


def notify_service_cycle(order_type, order, months):
    text = (
        "🔁 <b>Нагадування про сервіс</b>\n"
        f"Період: {_e(months)} міс.\n"
        f"Тип заявки: {_e(order_type)}\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Клієнт: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>"
    )
    send_message(text)
