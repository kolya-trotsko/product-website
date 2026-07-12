import json
import os
from pathlib import Path
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured

# Django 5.2 settings for the KS KLIMAT KH project.
BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_ENVIRONMENTS = {"local", "development", "dev", "test"}
DJANGO_ENV = os.getenv("DJANGO_ENV", "local").lower()


def env_bool(name, default="False"):
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


def env_int(name, default):
    value = os.getenv(name, str(default))
    try:
        return int(value)
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} must be an integer.") from exc


def env_list(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def require_env(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"{name} environment variable is required.")
    return value


def validate_site_url(value):
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ImproperlyConfigured("SITE_URL must be an absolute HTTPS URL in production.")


DEBUG = env_bool("DEBUG", "True" if DJANGO_ENV in LOCAL_ENVIRONMENTS else "False")
SECRET_KEY = os.getenv("SECRET_KEY", "")
UNSAFE_SECRET_KEYS = {
    "",
    "dev-insecure-secret-key-change-me",
    "django-insecure-change-me",
    "change-me",
}
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-insecure-secret-key-change-me"  # nosec B105
    else:
        raise ImproperlyConfigured("SECRET_KEY environment variable must be set when DEBUG is False.")
if not DEBUG and SECRET_KEY in UNSAFE_SECRET_KEYS:
    raise ImproperlyConfigured("SECRET_KEY is a known unsafe placeholder and cannot be used in production.")

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    [
        "127.0.0.1",
        "localhost",
        "192.168.1.14",
    ],
)
if not DEBUG and (not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS):
    raise ImproperlyConfigured("ALLOWED_HOSTS must be explicitly set and non-empty in production.")


def load_google_oauth_app(base_dir):
    client_id = os.getenv("GOOGLE_OAUTH2_CLIENT_ID", "")
    secret = os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET", "")
    if client_id and secret:
        return client_id, secret
    secret_file = os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET_FILE", "")
    if not secret_file:
        default_path = base_dir / "secrets" / "google_oauth_client.json"
        if default_path.exists():
            secret_file = str(default_path)
    if secret_file:
        try:
            with open(secret_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            web = data.get("web", data)
            client_id = client_id or web.get("client_id", "")
            secret = secret or web.get("client_secret", "")
        except (OSError, json.JSONDecodeError):
            pass
    return client_id, secret


APPS = [
    "catalog",
    "service",
    "ks_klimat_kh",
]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "company_info",
] + APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ks_klimat_kh.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "ks_klimat_kh/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "ks_klimat_kh.context_processors.site_metadata",
                "ks_klimat_kh.context_processors.company_contacts",
            ],
        },
    },
]

WSGI_APPLICATION = "ks_klimat_kh.wsgi.application"


DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")
if DB_ENGINE == "django.db.backends.sqlite3":
    DB_NAME = os.getenv("DB_NAME", str(BASE_DIR / "db.sqlite3"))
else:
    DB_NAME = require_env("DB_NAME") if not DEBUG else os.getenv("DB_NAME", "")
    if not DEBUG:
        require_env("DB_USER")
        require_env("DB_HOST")

DATABASES = {
    "default": {
        "ENGINE": DB_ENGINE,
        "NAME": DB_NAME,
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "uk"

TIME_ZONE = "Europe/Kyiv"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"

STATICFILES_DIRS = [os.path.join(BASE_DIR, app, "static") for app in APPS]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STORAGES = {
    "default": {
        "BACKEND": os.getenv("DEFAULT_FILE_STORAGE", "django.core.files.storage.FileSystemStorage"),
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
WHITENOISE_MANIFEST_STRICT = env_bool("WHITENOISE_MANIFEST_STRICT", "False" if DEBUG else "True")

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", "True")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@localhost")

SITE_NAME = os.getenv("SITE_NAME", "KS KLIMAT KH")
SITE_URL = os.getenv("SITE_URL", "")
if not DEBUG:
    SITE_URL = require_env("SITE_URL")
    validate_site_url(SITE_URL)

SITE_ID = 1
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/service/home/"
LOGOUT_REDIRECT_URL = "/service/home/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

GOOGLE_OAUTH2_CLIENT_ID, GOOGLE_OAUTH2_CLIENT_SECRET = load_google_oauth_app(BASE_DIR)

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_OAUTH2_CLIENT_ID,
            "secret": GOOGLE_OAUTH2_CLIENT_SECRET,
            "key": "",
        }
    }
}

REDIS_URL = os.getenv("REDIS_URL", "").strip()
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ks-klimat-local",
    }
}
if REDIS_URL:
    CACHES["default"] = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }

RATE_LIMITS = {
    "review": {"limit": 3, "window": 60},
    "conditioner_order": {"limit": 5, "window": 60},
    "service_order": {"limit": 5, "window": 60},
    "home_order": {"limit": 5, "window": 60},
}
RATE_LIMITING_ENABLED = env_bool("RATE_LIMITING_ENABLED", "True")
if not DEBUG and RATE_LIMITING_ENABLED and not REDIS_URL:
    raise ImproperlyConfigured("REDIS_URL is required in production when rate limiting is enabled.")

USE_X_FORWARDED_FOR = env_bool("USE_X_FORWARDED_FOR", "False")
TRUST_PROXY_HEADERS = env_bool("TRUST_PROXY_HEADERS", "False")
TELEGRAM_NOTIFICATIONS_ENABLED = env_bool("TELEGRAM_NOTIFICATIONS_ENABLED", "False")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_CHAT_IDS = env_list("TELEGRAM_ADMIN_CHAT_IDS", [])
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
TELEGRAM_WEBHOOK_MAX_BYTES = env_int("TELEGRAM_WEBHOOK_MAX_BYTES", 65536)

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", "True")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", 31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", "False")
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", "False")
    if env_bool("SECURE_PROXY_SSL_HEADER_ENABLED", "False"):
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(levelname)s %(asctime)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
