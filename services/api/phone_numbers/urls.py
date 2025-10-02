from __future__ import annotations

from django.urls import path

from .views import HealthzView, MetricsView, PrefixListView, ReadyView, SearchView

urlpatterns = [
    path("prefixes", PrefixListView.as_view(), name="prefixes"),
    path("search", SearchView.as_view(), name="search"),
    path("healthz", HealthzView.as_view(), name="healthz"),
    path("ready", ReadyView.as_view(), name="ready"),
    path("metrics", MetricsView.as_view(), name="metrics"),
]
