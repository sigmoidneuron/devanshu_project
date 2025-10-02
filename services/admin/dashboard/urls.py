from __future__ import annotations

from django.urls import path

from .views import auth as auth_views
from .views import docs as docs_views
from .views import health as health_views
from .views import numbers as number_views
from .views import upload as upload_views

urlpatterns = [
    path("", number_views.home_redirect, name="home"),
    path("login/", auth_views.login_view, name="login"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("settings", auth_views.change_credentials_view, name="settings"),
    path("numbers", number_views.numbers_list_view, name="numbers_list"),
    path("numbers/action", number_views.numbers_post_view, name="numbers_action"),
    path("upload", upload_views.upload_view, name="upload"),
    path("v1/auth/login", auth_views.LoginApiView.as_view(), name="api-login"),
    path("v1/auth/logout", auth_views.LogoutApiView.as_view(), name="api-logout"),
    path("v1/auth/me", auth_views.MeApiView.as_view(), name="api-me"),
    path("v1/auth/change-credentials", auth_views.ChangeCredentialsApiView.as_view(), name="api-change-credentials"),
    path("v1/numbers", number_views.NumbersApiView.as_view(), name="api-numbers"),
    path("v1/numbers/<uuid:pk>", number_views.NumberDetailApiView.as_view(), name="api-number-detail"),
    path("v1/numbers/bulk-upload", upload_views.BulkUploadApiView.as_view(), name="api-bulk-upload"),
    path("v1/healthz", health_views.HealthzView.as_view(), name="admin-healthz"),
    path("v1/ready", health_views.ReadyView.as_view(), name="admin-ready"),
    path("v1/schema/", docs_views.schema_view, name="admin-schema"),
    path("v1/docs/", docs_views.swagger_view, name="admin-swagger"),
]
