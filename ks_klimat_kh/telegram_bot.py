import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from catalog.models import ConditionerOrder
from ks_klimat_kh.telegram_notify import send_message
from service.models import (
    BotLead,
    Order,
    ServiceOrder,
    ORDER_STATUS_DONE,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_NEW,
)


ORDER_MODEL_MAP = {
    "home": Order,
    "service": ServiceOrder,
    "catalog": ConditionerOrder,
}


def _admin_ids():
    ids = []
    for value in getattr(settings, "TELEGRAM_ADMIN_CHAT_IDS", []):
        try:
            ids.append(int(value))
        except (TypeError, ValueError):
            continue
    return set(ids)


def _is_admin(user_id):
    return user_id in _admin_ids()


def _format_order_line(prefix, order):
    return f"[{prefix} #{order.id}] {order.name} | {order.phone} | {order.status}"


def _list_by_status(status):
    rows = []
    for prefix, model in ORDER_MODEL_MAP.items():
        rows.extend((prefix, obj) for obj in model.objects.filter(status=status).order_by("-created_at")[:5])
    return rows


def _handle_assign(chat_id, text):
    parts = text.split()
    if len(parts) != 4:
        send_message("Формат: /assign <home|service|catalog> <order_id> <@username>", chat_id=chat_id)
        return

    _, order_type, order_id_raw, username_raw = parts
    order_type = order_type.lower()
    model = ORDER_MODEL_MAP.get(order_type)
    if not model:
        send_message("Невірний тип заявки. Доступно: home, service, catalog.", chat_id=chat_id)
        return
    if not order_id_raw.isdigit():
        send_message("order_id має бути числом.", chat_id=chat_id)
        return

    username = username_raw.lstrip("@")
    user_model = get_user_model()
    manager = user_model.objects.filter(username=username).first()
    if not manager:
        send_message("Менеджера з таким username не знайдено.", chat_id=chat_id)
        return

    order = model.objects.filter(id=int(order_id_raw)).first()
    if not order:
        send_message("Заявку не знайдено.", chat_id=chat_id)
        return

    order.manager = manager
    order.status = ORDER_STATUS_IN_PROGRESS
    order.save(update_fields=["manager", "status", "updated_at"])
    send_message(f"Призначено {manager.username} на заявку {order_type} #{order.id}.", chat_id=chat_id)


def _create_bot_lead(user_id, username, full_name, intent, text):
    return BotLead.objects.create(
        telegram_user_id=user_id,
        telegram_username=username or "",
        full_name=full_name or "",
        intent=intent,
        message=text,
    )


def process_telegram_update(payload):
    message = payload.get("message") or {}
    chat = message.get("chat") or {}
    sender = message.get("from") or {}

    chat_id = chat.get("id")
    user_id = sender.get("id")
    text = (message.get("text") or "").strip()
    username = sender.get("username", "")
    full_name = " ".join(part for part in [sender.get("first_name", ""), sender.get("last_name", "")] if part).strip()

    if not chat_id or not user_id or not text:
        return

    text_lower = text.lower()
    if text_lower == "хочу консультацію":
        lead = _create_bot_lead(user_id, username, full_name, BotLead.INTENT_CONSULT, text)
        send_message(f"Дякуємо! Лід #{lead.id} на консультацію прийнято.", chat_id=chat_id)
        return
    if text_lower == "підібрати модель":
        lead = _create_bot_lead(user_id, username, full_name, BotLead.INTENT_PICK_MODEL, text)
        send_message(f"Дякуємо! Лід #{lead.id} на підбір моделі прийнято.", chat_id=chat_id)
        return

    if not text.startswith("/"):
        return

    if not _is_admin(user_id):
        send_message("Команди доступні лише адміну.", chat_id=chat_id)
        return

    if text.startswith("/assign"):
        _handle_assign(chat_id, text)
        return

    if text.startswith("/new"):
        rows = _list_by_status(ORDER_STATUS_NEW)
    elif text.startswith("/in_progress"):
        rows = _list_by_status(ORDER_STATUS_IN_PROGRESS)
    elif text.startswith("/done"):
        rows = _list_by_status(ORDER_STATUS_DONE)
    else:
        send_message("Доступні команди: /new, /in_progress, /done, /assign.", chat_id=chat_id)
        return

    if not rows:
        send_message("Заявок не знайдено.", chat_id=chat_id)
        return

    lines = ["Заявки:"]
    lines.extend(_format_order_line(prefix, order) for prefix, order in rows[:15])
    send_message("\n".join(lines), chat_id=chat_id)


@csrf_exempt
def telegram_webhook(request, secret):
    if not settings.TELEGRAM_NOTIFICATIONS_ENABLED:
        return HttpResponseForbidden("Telegram integration disabled.")
    if not settings.TELEGRAM_WEBHOOK_SECRET or secret != settings.TELEGRAM_WEBHOOK_SECRET:
        return HttpResponseForbidden("Invalid webhook secret.")
    if request.method != "POST":
        return HttpResponseBadRequest("POST only.")

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")

    process_telegram_update(payload)
    return JsonResponse({"ok": True})
