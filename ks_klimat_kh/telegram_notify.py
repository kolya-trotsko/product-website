import json
import logging
from html import escape
from urllib import error, request

from django.conf import settings


logger = logging.getLogger(__name__)


def _e(value):
    return escape(str(value), quote=True)


def _is_enabled():
    return (
        getattr(settings, "TELEGRAM_NOTIFICATIONS_ENABLED", False)
        and bool(getattr(settings, "TELEGRAM_BOT_TOKEN", ""))
        and bool(getattr(settings, "TELEGRAM_ADMIN_CHAT_IDS", []))
    )


def _send_message(text):
    if not _is_enabled():
        return

    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    for chat_id in settings.TELEGRAM_ADMIN_CHAT_IDS:
        payload = json.dumps(
            {
                "chat_id": chat_id,
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
            logger.warning("Failed to send telegram notification to %s: %s", chat_id, exc)


def notify_home_order(order, request_path=""):
    text = (
        "🆕 <b>Нове замовлення (Головна)</b>\n"
        f"ID: <code>{_e(order.id)}</code>\n"
        f"Ім'я: <b>{_e(order.name)}</b>\n"
        f"Телефон: <code>{_e(order.phone)}</code>\n"
        f"Тип: {_e(order.place)}\n"
        f"Сторінка: <code>{_e(request_path or order.source_page)}</code>"
    )
    _send_message(text)


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
    _send_message(text)


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
    _send_message(text)
