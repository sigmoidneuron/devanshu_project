from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


SECRET_KEY = get_env("DJANGO_SECRET_KEY", "unsafe-secret-key")
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
    "api.middleware.RequestIDMiddleware",
]

ROOT_URLCONF = "api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "api.wsgi.application"
ASGI_APPLICATION = "api.asgi.application"


def database_config() -> Dict[str, Any]:
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
            return {
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": name,
                }
            }
    if engine == "postgres" or engine == "postgresql":
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
    name = os.getenv("DATABASE_NAME", BASE_DIR / ".." / ".." / "data" / "api.sqlite3")
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(name),
        }
    }


DATABASES = database_config()

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ALLOWLIST", "").split(",") if origin.strip()]
CORS_ALLOW_CREDENTIALS = False

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "api.phone_numbers.throttles.PublicRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "public": os.getenv("RATE_LIMITS_PUBLIC", "60/min"),
    },
    "EXCEPTION_HANDLER": "api.utils.exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Phone Number Search API",
    "DESCRIPTION": "Public API for searching related phone numbers.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

cache_location = os.getenv(
    "CACHE_DIR",
    str((BASE_DIR / ".." / ".." / "data" / "cache_api").resolve()),
)
Path(cache_location).mkdir(parents=True, exist_ok=True)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": cache_location,
    }
}

RATELIMIT_USE_CACHE = "default"

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
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

PROMETHEUS_MULTIPROC_DIR = os.getenv("PROMETHEUS_MULTIPROC_DIR")

SILENCED_SYSTEM_CHECKS = [
    "django_ratelimit.E003",
    "django_ratelimit.W001",
]
