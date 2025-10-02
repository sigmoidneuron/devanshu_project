from __future__ import annotations

import pytest

from shared.core.models import Number


@pytest.mark.django_db
def test_search_returns_related_numbers(api_client):
    query = Number.objects.create(area_code="415", phone_number="5551234", cost=200)
    Number.objects.create(area_code="415", phone_number="5551235", cost=150)
    Number.objects.create(area_code="415", phone_number="5552234", cost=180)
    Number.objects.create(area_code="212", phone_number="5551234", cost=90)

    response = api_client.get("/v1/search", {"area_code": "415", "number": "5551234"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) >= 2
    assert all(item["area_code"] in {"415", "212"} for item in data["results"])
    assert all(item["full_number"] != query.full_number for item in data["results"])


@pytest.mark.django_db
def test_search_validation(api_client):
    response = api_client.get("/v1/search", {"area_code": "41", "number": "abc"})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
