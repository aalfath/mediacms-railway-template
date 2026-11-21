# MediaCMS local settings for Railway (replaces deploy/docker/local_settings.py).
import os
from urllib.parse import unquote, urlparse


def _bool(name, default):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


FRONTEND_HOST = os.getenv("FRONTEND_HOST", "http://localhost").rstrip("/")
PORTAL_NAME = os.getenv("PORTAL_NAME", "MediaCMS")
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
CELERY_TIMEZONE = TIME_ZONE
DEBUG = os.getenv("DEBUG", "False") == "True"

# Postgres: DATABASE_URL (Railway) or the upstream POSTGRES_* variables
_db = urlparse(os.getenv("DATABASE_URL", ""))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": (_db.path or "").lstrip("/") or os.getenv("POSTGRES_NAME", "mediacms"),
        "HOST": _db.hostname or os.getenv("POSTGRES_HOST", "db"),
        "PORT": str(_db.port or os.getenv("POSTGRES_PORT", "5432")),
        "USER": unquote(_db.username or "") or os.getenv("POSTGRES_USER", "mediacms"),
        "PASSWORD": unquote(_db.password or "") or os.getenv("POSTGRES_PASSWORD", ""),
        "OPTIONS": {
            "pool": {
                "min_size": 2,
                "max_size": 8,
                "timeout": 10,
                "max_lifetime": 30 * 60,
                "max_idle": 10 * 60,
            }
        },
    }
}

# Redis: REDIS_LOCATION, else REDIS_URL (Railway) on database 1
REDIS_LOCATION = os.getenv("REDIS_LOCATION", "")
if not REDIS_LOCATION:
    _redis = os.getenv("REDIS_URL", "redis://redis:6379").rstrip("/")
    REDIS_LOCATION = _redis if urlparse(_redis).path not in ("", "/") else _redis + "/1"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# CELERY STUFF
BROKER_URL = REDIS_LOCATION
CELERY_RESULT_BACKEND = BROKER_URL

MP4HLS_COMMAND = "/home/mediacms.io/bento4/bin/mp4hls"

# Railway terminates HTTPS at its edge and forwards X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [FRONTEND_HOST] if FRONTEND_HOST.startswith("https://") else []
if FRONTEND_HOST.startswith("https://"):
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Public sign-up is closed by default; set USERS_CAN_SELF_REGISTER=True to open it
USERS_CAN_SELF_REGISTER = _bool("USERS_CAN_SELF_REGISTER", False)
REGISTER_ALLOWED = USERS_CAN_SELF_REGISTER
GLOBAL_LOGIN_REQUIRED = _bool("GLOBAL_LOGIN_REQUIRED", False)

# Optional SMTP (password resets, notifications). Without EMAIL_HOST no mail is sent.
if os.getenv("EMAIL_HOST"):
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = _bool("EMAIL_USE_TLS", True)
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
    ADMIN_EMAIL_LIST = [os.getenv("ADMIN_EMAIL", DEFAULT_FROM_EMAIL)]
else:
    EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
