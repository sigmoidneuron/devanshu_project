from __future__ import annotations

import uuid

from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    header = "HTTP_X_REQUEST_ID"

    def process_request(self, request):
        request_id = request.META.get(self.header)
        if not request_id:
            request_id = uuid.uuid4().hex
        request.request_id = request_id
        request.META[self.header] = request_id

    def process_response(self, request, response):
        request_id = getattr(request, "request_id", None)
        if request_id:
            response["X-Request-ID"] = request_id
        return response
