from __future__ import annotations

import logging
import time

from django.core.cache import cache
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge, generate_latest

from shared.core.models import Number
from shared.core.search import rank_related_numbers

from .serializers import PrefixSerializer, SearchQuerySerializer, SearchResultSerializer

logger = logging.getLogger(__name__)
PROCESS_START = time.time()


class PrefixListView(APIView):
    def get(self, request: HttpRequest) -> Response:
        try:
            limit = min(max(int(request.GET.get("limit", 100)), 1), 500)
        except ValueError:
            limit = 100
        try:
            offset = max(int(request.GET.get("offset", 0)), 0)
        except ValueError:
            offset = 0
        query = request.GET.get("q")

        cache_key = f"prefixes:{limit}:{offset}:{query}"
        data = cache.get(cache_key)
        if not data:
            qs = Number.objects.values("area_code").annotate(count=Count("id"))
            if query:
                qs = qs.filter(area_code__startswith=query)
            qs = qs.order_by("-count", "area_code")
            sliced = qs[offset : offset + limit]
            serializer = PrefixSerializer(sliced, many=True)
            data = {
                "results": serializer.data,
                "count": qs.count(),
                "limit": limit,
                "offset": offset,
            }
            cache.set(cache_key, data, timeout=60)
        return Response(data)


class SearchView(APIView):
    def get(self, request: HttpRequest) -> Response:
        serializer = SearchQuerySerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        area_code = serializer.validated_data["area_code"]
        number = serializer.validated_data["number"]

        results = rank_related_numbers(Number.objects.all(), area_code, number, limit=10)
        payload = {"results": SearchResultSerializer(results, many=True).data}
        return Response(payload)


class HealthzView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def get(self, request: HttpRequest) -> Response:
        uptime = time.time() - PROCESS_START
        data = {
            "ok": True,
            "service": "api",
            "uptime": uptime,
            "timestamp": timezone.now().isoformat(),
        }
        return Response(data)


class ReadyView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def get(self, request: HttpRequest) -> Response:
        try:
            Number.objects.exists()
        except Exception as exc:  # pragma: no cover - exercised via readiness check
            logger.exception("Database readiness check failed", exc_info=exc)
            return Response({"ok": False}, status=503)
        return Response({"ok": True})


class MetricsView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def get(self, request: HttpRequest) -> HttpResponse:
        registry = CollectorRegistry()
        number_count = Gauge("phone_numbers_total", "Total phone numbers", registry=registry)
        number_count.set(Number.objects.count())
        data = generate_latest(registry)
        return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)
