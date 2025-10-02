from __future__ import annotations

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

schema_view = SpectacularAPIView.as_view(urlconf="dashboard.urls")
swagger_view = SpectacularSwaggerView.as_view(url_name="admin-schema")
