from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

from .startup import setup_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard.settings")

application = setup_application(get_asgi_application)
