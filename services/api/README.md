# API Service

Django REST Framework project exposing public endpoints for area code discovery and related phone number search.

## Local development

```bash
export DJANGO_SETTINGS_MODULE=api.settings
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Key endpoints

- `GET /v1/prefixes`
- `GET /v1/search?area_code=AAA&number=BBBBBBB`
- `GET /v1/healthz`
- `GET /v1/ready`
- `GET /v1/docs/`
