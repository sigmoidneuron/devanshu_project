"""Custom schema extensions for the public API."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class SessionCookieScheme(OpenApiAuthenticationExtension):
    target_class = "rest_framework.authentication.SessionAuthentication"
    name = "SessionCookie"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "sessionid",
        }
