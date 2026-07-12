import math
import time
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache


@dataclass(frozen=True)
class RateLimitResult:
    limited: bool
    retry_after: int = 0


def get_client_ip(request):
    use_forwarded = getattr(settings, "USE_X_FORWARDED_FOR", False) and getattr(settings, "TRUST_PROXY_HEADERS", False)
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if use_forwarded and forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _rate_key(request, action):
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return f"rl:{action}:user:{user.pk}"
    return f"rl:{action}:ip:{get_client_ip(request)}"


def check_rate_limit(request, action):
    if not getattr(settings, "RATE_LIMITING_ENABLED", True):
        return RateLimitResult(False)
    limits = getattr(settings, "RATE_LIMITS", {})
    config = limits.get(action)
    if not config:
        return RateLimitResult(False)
    limit = int(config.get("limit", 0))
    window = int(config.get("window", 0))
    if limit <= 0 or window <= 0:
        return RateLimitResult(False)

    key = _rate_key(request, action)
    reset_key = f"{key}:reset"
    now = time.time()
    if cache.add(key, 1, window):
        cache.set(reset_key, now + window, window)
        return RateLimitResult(False)
    try:
        current = cache.incr(key)
    except ValueError:
        cache.set(key, 1, window)
        cache.set(reset_key, now + window, window)
        return RateLimitResult(False)

    if current > limit:
        reset_at = cache.get(reset_key) or (now + window)
        return RateLimitResult(True, max(1, math.ceil(reset_at - now)))
    return RateLimitResult(False)


def is_rate_limited(request, action):
    return check_rate_limit(request, action).limited
