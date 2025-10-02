# Admin Service

Django-based admin dashboard with HTML templates and JSON endpoints for managing phone numbers.

## Local development

```bash
export DJANGO_SETTINGS_MODULE=dashboard.settings
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```

## Key URLs

- `/login/`
- `/numbers`
- `/upload`
- `/settings`
- `/v1/auth/login`
- `/v1/numbers`
- `/v1/healthz`
- `/v1/docs/`
