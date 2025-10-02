from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_healthz(api_client):
    response = api_client.get("/v1/healthz")
    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.django_db
def test_ready(api_client):
    response = api_client.get("/v1/ready")
    assert response.status_code == 200
    assert response.json()["ok"] is True
