from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc: Exception, context: dict[str, Any]):
    response = drf_exception_handler(exc, context)
    if response is None:
        return Response(
            {"error": {"code": "server_error", "message": "An unexpected error occurred."}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    error_detail = response.data
    if isinstance(error_detail, dict) and "detail" in error_detail:
        message = error_detail["detail"]
        error_code = getattr(getattr(exc, "default_code", None), "value", None) or getattr(exc, "default_code", "error")
        response.data = {"error": {"code": error_code, "message": str(message)}}
    elif isinstance(error_detail, list):
        response.data = {"error": {"code": "error", "message": error_detail[0]}}
    else:
        response.data = {"error": {"code": "error", "message": "Validation error."}}
    return response
