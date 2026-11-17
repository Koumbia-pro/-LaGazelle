import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

CACHES = {
    "default": {
        "BACKEND": os.getenv(
            "CACHE_BACKEND",
            "django.core.cache.backends.db.DatabaseCache",
        ),
        "LOCATION": os.getenv("CACHE_LOCATION", CACHE_TABLE_NAME),
    }
}

if not SECRET_KEY or SECRET_KEY.startswith("django-insecure-") or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("SECRET_KEY robuste d’au moins 50 caractères obligatoire en production.")
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ["localhost", "127.0.0.1"] or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS doit contenir les domaines publics en production.")
if not HCAPTCHA_SITE_KEY or not HCAPTCHA_SECRET_KEY:
    raise ImproperlyConfigured("HCAPTCHA_SITE_KEY et HCAPTCHA_SECRET_KEY sont obligatoires en production.")
if EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend" or not EMAIL_HOST:
    raise ImproperlyConfigured("Un SMTP de production doit être configuré.")
if not PROJECT_NOTIFICATION_EMAIL:
    raise ImproperlyConfigured("PROJECT_NOTIFICATION_EMAIL est obligatoire en production.")
if "locmem" in CACHES["default"]["BACKEND"].lower():
    raise ImproperlyConfigured("Le cache local n’est pas autorisé en production.")

DEBUG = False
TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "True").lower() in {"1", "true", "yes"}
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 60 * 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() in {"1", "true", "yes"}
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
