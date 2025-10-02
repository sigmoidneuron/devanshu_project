from __future__ import annotations

import pytest

from shared.core.models import Number


@pytest.mark.django_db
def test_prefixes_endpoint_returns_counts(api_client):
    Number.objects.create(area_code="212", phone_number="1234567", cost=99)
    Number.objects.create(area_code="212", phone_number="1234568", cost=199)
    Number.objects.create(area_code="305", phone_number="7654321", cost=149)

    response = api_client.get("/v1/prefixes")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    first = data["results"][0]
    assert first["area_code"] in {"212", "305"}
