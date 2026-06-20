from django.conf import settings
from django.core.cache import cache


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def is_rate_limited(request, action):
    limits = getattr(settings, "RATE_LIMITS", {})
    config = limits.get(action)
    if not config:
        return False
    limit = int(config.get("limit", 0))
    window = int(config.get("window", 0))
    if limit <= 0 or window <= 0:
        return False
    key = f"rl:{action}:{_client_ip(request)}"
    current = cache.get(key)
    if current is None:
        cache.set(key, 1, window)
        return False
    if current >= limit:
        return True
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, current + 1, window)
    return False
