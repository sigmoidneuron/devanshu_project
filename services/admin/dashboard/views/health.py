from __future__ import annotations

import time

from django.http import HttpRequest
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.core.models import Number


PROCESS_START = time.time()


class HealthzView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: HttpRequest) -> Response:
        return Response(
            {
                "ok": True,
                "service": "admin",
                "uptime": time.time() - PROCESS_START,
                "timestamp": timezone.now().isoformat(),
            }
        )


class ReadyView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: HttpRequest) -> Response:
        try:
            Number.objects.exists()
        except Exception:
            return Response({"ok": False}, status=503)
        return Response({"ok": True})
