from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)


def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing environment variable {name}")
    return value


SECRET_KEY = env("DJANGO_SECRET_KEY", "unsafe-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "localhost").split(",") if host.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "django_ratelimit",
    "shared.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "dashboard.middleware.RequestIDMiddleware",
]

ROOT_URLCONF = "dashboard.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "dashboard.wsgi.application"
ASGI_APPLICATION = "dashboard.asgi.application"


def database_config():
    url = os.getenv("DATABASE_URL")
    engine = os.getenv("DATABASE_ENGINE", "sqlite").lower()
    if url:
        parsed = urlparse(url)
        if parsed.scheme.startswith("postgres"):
            return {
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": parsed.path.lstrip("/"),
                    "USER": parsed.username or "",
                    "PASSWORD": parsed.password or "",
                    "HOST": parsed.hostname or "",
                    "PORT": str(parsed.port or ""),
                }
            }
        if parsed.scheme.startswith("sqlite"):
            db_path = parsed.path or parsed.netloc
            if db_path.startswith("/"):
                name = db_path
            else:
                name = str(BASE_DIR / db_path)
            return {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": name}}
    if engine.startswith("postgres"):
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.getenv("DATABASE_NAME", "phone_numbers"),
                "USER": os.getenv("DATABASE_USER", "postgres"),
                "PASSWORD": os.getenv("DATABASE_PASSWORD", "postgres"),
                "HOST": os.getenv("DATABASE_HOST", "db"),
                "PORT": os.getenv("DATABASE_PORT", "5432"),
            }
        }
    name = os.getenv("DATABASE_NAME", BASE_DIR / ".." / ".." / "data" / "admin.sqlite3")
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(name),
        }
    }


DATABASES = database_config()

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ALLOWLIST", "").split(",") if origin.strip()]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Phone Number Admin API",
    "DESCRIPTION": "Admin endpoints for managing phone numbers.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/numbers"
SESSION_COOKIE_NAME = "admin_sessionid"
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() in {"1", "true", "yes"}
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "true").lower() in {"1", "true", "yes"}
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "admin-cache",
    }
}

RATELIMIT_USE_CACHE = "default"
LOGIN_RATE_LIMIT = os.getenv("RATE_LIMITS_LOGIN", "10/15m")
ADMIN_API_RATE_LIMIT = os.getenv("RATE_LIMITS_ADMIN", "120/min")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
